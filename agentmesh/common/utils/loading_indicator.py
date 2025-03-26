import threading
import time
import sys
import itertools


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
    
    def start(self):
        """Start the loading animation."""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._animate)
            self.thread.daemon = True
            self.thread.start()
    
    def stop(self):
        """Stop the loading animation."""
        if self.is_running:
            self.is_running = False
            if self.thread:
                self.thread.join()
