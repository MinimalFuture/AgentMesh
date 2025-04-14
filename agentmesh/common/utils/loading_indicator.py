import threading
import time
import sys
import itertools
import os


class LoadingIndicator:
    """
    A utility class for displaying a loading animation in the console.
    """

    def __init__(self, message="Loading", animation_type="spinner"):
        """
        Initialize the loading indicator.
        
        :param message: The message to display alongside the animation.
        :param animation_type: The type of animation to display ('spinner', 'dots', 'bar', 'thinking').
        """
        self.message = message
        self.animation_type = animation_type
        self.is_running = False
        self.thread = None

        # Define different animation styles
        self.animations = {
            "spinner": itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']),
            "dots": itertools.cycle(['.  ', '.. ', '...', '   ']),
            "bar": itertools.cycle(['[=  ]', '[== ]', '[===]', '[ ==]', '[  =]', '[   ]']),
            "thinking": itertools.cycle(['🧠  ', '🧠. ', '🧠..', '🧠...'])
        }

        # Use the specified animation or default to spinner
        self.animation = self.animations.get(animation_type, self.animations["spinner"])

        # Check if we're in a Docker environment
        self.use_threading = not (os.environ.get("DOCKER_CONTAINER", "").lower() in ("true", "1"))

    def _animate(self):
        """The animation function that runs in a separate thread."""
        while self.is_running:
            char = next(self.animation)
            sys.stdout.write(f'\r{char} {self.message}')
            sys.stdout.flush()
            time.sleep(0.1)

        # Clear the line when animation stops
        sys.stdout.write('\r' + ' ' * (len(self.message) + 10) + '\r')
        sys.stdout.flush()

    def _animate_simple(self):
        """A simpler animation that doesn't use threading."""
        char = next(self.animation)
        sys.stdout.write(f'\r{char} {self.message}')
        sys.stdout.flush()

    def start(self):
        """Start the loading animation."""
        if not self.is_running:
            self.is_running = True

            # Use threading only if it's enabled
            if self.use_threading:
                try:
                    self.thread = threading.Thread(target=self._animate)
                    self.thread.daemon = True
                    self.thread.start()
                except (RuntimeError, ThreadError):
                    # If thread creation fails, fall back to simple mode
                    self._animate_simple()
            else:
                # Just show a static indicator without animation
                sys.stdout.write(f'\r⏳ {self.message}')
                sys.stdout.flush()

    def stop(self):
        """Stop the loading animation."""
        if self.is_running:
            self.is_running = False
            if self.thread and self.use_threading:
                try:
                    self.thread.join(timeout=0.5)  # Add timeout to prevent hanging
                except Exception:
                    pass  # Ignore any errors when stopping

            # Clear the line
            sys.stdout.write('\r' + ' ' * (len(self.message) + 10) + '\r')
            sys.stdout.flush()
