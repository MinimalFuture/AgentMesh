import json


class XmlResParser:
    """
    A utility class for parsing streaming XML responses, supporting the handling of content that includes < > characters.
    """

    def __init__(self):
        # Store parsed data
        self.parsed_data = {}

        # Current tag and content being processed
        self.current_tag = None
        self.current_content = ""

        # State flags
        self.in_tag = False
        self.in_start_tag = False
        self.in_end_tag = False

        # Tag buffer
        self.tag_buffer = ""

        # List of valid tags (including root tags)
        self.valid_tags = ["thought", "action", "action_input", "final_answer", "response"]

        # Content tags we care about (excluding root tags)
        self.content_tags = ["thought", "action", "action_input", "final_answer"]

        # Tags that require streaming output
        self.streaming_tags = ["thought", "final_answer"]

        # Whether tags have been printed
        self.printed_tags = {tag: False for tag in self.content_tags}

        # Complete raw response
        self.raw_response = ""

        # State machine states
        self.STATE_TEXT = 0
        self.STATE_TAG_START = 1
        self.STATE_TAG_NAME = 2
        self.STATE_TAG_END = 3
        self.state = self.STATE_TEXT

        # Escape state
        self.escaped = False

        # Whether inside the root tag
        self.in_root = False

        # Emoji mapping
        self.emoji_map = {
            "thought": "🧠",
            "action": "🛠️",
            "action_input": "",  # No additional emoji needed
            "final_answer": "💬"
        }

        # Whether tag content is empty or null
        self.is_null_content = {tag: False for tag in self.content_tags}

        # Cache tag content for post-processing
        self.tag_contents = {tag: "" for tag in self.content_tags}

        # For handling leading whitespace in final_answer
        self.leading_whitespace_removed = False
        self.in_final_answer = False
        self.final_answer_started = False

    def process_chunk(self, chunk):
        """Process a chunk of streaming content."""
        self.raw_response += chunk

        # Process character by character
        for char in chunk:
            self._process_char(char)

    def _process_char(self, char):
        """Process a single character."""
        # State machine processing
        if self.state == self.STATE_TEXT:
            if char == '<':
                self.state = self.STATE_TAG_START
                self.tag_buffer = ""
                self.in_start_tag = True
                self.in_end_tag = False
            else:
                # Inside tag content
                if self.current_tag and self.current_tag in self.content_tags:
                    self.current_content += char

                    # Directly print content for tags that require streaming output
                    if self.current_tag in self.streaming_tags:
                        # Special handling for leading whitespace in final_answer
                        if self.current_tag == "final_answer":
                            if not self.final_answer_started:
                                # Skip leading whitespace until the first non-whitespace character is encountered
                                if not char.isspace():
                                    self.final_answer_started = True
                                    print(char, end="", flush=True)
                                # Otherwise, skip whitespace characters
                            else:
                                # Already started outputting content, print all characters directly
                                print(char, end="", flush=True)
                        else:
                            # Print other tags directly
                            print(char, end="", flush=True)

        elif self.state == self.STATE_TAG_START:
            if char == '/':
                self.in_end_tag = True
                self.in_start_tag = False
                self.state = self.STATE_TAG_NAME
            elif char.isalpha() or char == '_':
                self.tag_buffer += char
                self.state = self.STATE_TAG_NAME
            else:
                # Not a valid tag start, return to text state
                self._handle_invalid_tag('<' + char)
                self.state = self.STATE_TEXT

        elif self.state == self.STATE_TAG_NAME:
            if char == '>':
                self.state = self.STATE_TEXT
                self._handle_tag_complete()
            elif char.isalnum() or char == '_':
                self.tag_buffer += char
            else:
                # Invalid character in tag name, treat as normal text
                self._handle_invalid_tag('<' + ('/' if self.in_end_tag else '') + self.tag_buffer + char)
                self.state = self.STATE_TEXT

    def _handle_tag_complete(self):
        """Handle complete tag."""
        # Check if it is a valid tag
        if self.tag_buffer in self.valid_tags:
            # Special handling for response tag
            if self.tag_buffer == "response":
                if not self.in_end_tag:
                    self.in_root = True
                else:
                    self.in_root = False
                return

            if self.in_end_tag:
                # End tag
                if self.current_tag == self.tag_buffer:
                    # Save current tag content and check for null
                    content = self.current_content.strip()
                    self.parsed_data[self.current_tag] = content
                    self.tag_contents[self.current_tag] = content

                    # Check if content is null or empty
                    self.is_null_content[self.current_tag] = (
                            content.lower() == "null" or
                            content == "" or
                            content.isspace()
                    )

                    # Reset state
                    if self.current_tag == "final_answer":
                        self.in_final_answer = False
                        self.final_answer_started = False

                    self.current_tag = None
                    self.current_content = ""
                else:
                    # Tag mismatch, treat as normal text
                    self._handle_invalid_tag('</' + self.tag_buffer + '>')
            else:
                # Start tag
                self.current_tag = self.tag_buffer
                self.current_content = ""

                # Set state
                if self.current_tag == "final_answer":
                    self.in_final_answer = True
                    self.final_answer_started = False

                # Print tag name
                if not self.printed_tags[self.tag_buffer]:
                    # Use emoji format
                    emoji = self.emoji_map.get(self.tag_buffer, "")

                    if self.tag_buffer == "thought":
                        print(f"{emoji} ", end="", flush=True)
                    elif self.tag_buffer == "final_answer":
                        # Add streaming output tag for final_answer
                        print(f"\n{emoji} ", end="", flush=True)
                    # Action is handled at the end tag

                    self.printed_tags[self.tag_buffer] = True
        else:
            # Not a valid tag, treat as normal text
            tag_text = '<' + ('/' if self.in_end_tag else '') + self.tag_buffer + '>'
            self._handle_invalid_tag(tag_text)

    def _handle_invalid_tag(self, tag_text):
        """Handle invalid tag."""
        if self.current_tag and self.current_tag in self.content_tags:
            # Inside tag content, treat invalid tag as part of the content
            self.current_content += tag_text

            # Directly print content for tags that require streaming output
            if self.current_tag in self.streaming_tags:
                # Special handling for final_answer
                if self.current_tag == "final_answer" and not self.final_answer_started:
                    # If content has not started outputting, do not print
                    pass
                else:
                    print(tag_text, end="", flush=True)
        elif any(self.printed_tags.values()):
            # Not inside any tag, but output has started, treat invalid tag as normal text
            print(tag_text, end="", flush=True)

    def get_parsed_data(self):
        """Get parsing results."""
        result = self.parsed_data.copy()

        # Handle action and action_input
        if "action" in result and not self.is_null_content["action"]:
            action_content = result["action"].strip()

            # If action is not null, print action and action_input
            if "action_input" in result:
                action_input_content = result["action_input"].strip()

                try:
                    # Attempt to parse JSON
                    if action_input_content.startswith("{"):
                        action_input_json = json.loads(action_input_content)
                        result["action_input"] = action_input_json
                        # Print action and action_input
                        print(
                            f"\n{self.emoji_map['action']} {action_content}: {json.dumps(action_input_json, ensure_ascii=False)}")
                    # If it is "null" or empty, set to empty dictionary
                    elif action_input_content.lower() in ["null", ""]:
                        result["action_input"] = {}
                        # Print only action
                        print(f"\n{self.emoji_map['action']} {action_content}")
                    else:
                        # Print action and action_input
                        print(f"\n{self.emoji_map['action']} {action_content}: {action_input_content}")
                except json.JSONDecodeError:
                    # JSON parsing failed, keep as is
                    print(f"\n{self.emoji_map['action']} {action_content}: {action_input_content}")
            else:
                # No action_input, print only action
                print(f"\n{self.emoji_map['action']} {action_content}")

        # Handle final_answer - now only need to handle null values, as content has already been streamed
        if "final_answer" in result:
            final_answer_content = result["final_answer"].strip()

            if final_answer_content.lower() == "null":
                result["final_answer"] = None
            elif final_answer_content == "":
                # Empty content
                pass
            # No longer need to print final_answer, as it has already been streamed

        return result

    def get_raw_response(self):
        """Get raw response."""
        return self.raw_response
