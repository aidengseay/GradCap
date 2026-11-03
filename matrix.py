# ==============================================================================
# Matrix Imports
# ==============================================================================

import time
import board
import displayio
import framebufferio
import rgbmatrix
import terminalio

from adafruit_display_text import label

# ==============================================================================
# Matrix Constants
# ==============================================================================

SCROLL_INTERVAL = 0.04  # Seconds per pixel
WIDTH = 32
HEIGHT = 32

# ==============================================================================
# Matrix Class
# ==============================================================================

class MatrixController:

    # -----------------------------
    # Initialize the matrix
    # -----------------------------

    def __init__(self):

        # Initialize the pins for the RGB LED Matrix

        displayio.release_displays()

        self.matrix = rgbmatrix.RGBMatrix(
            width=WIDTH,
            height=HEIGHT,
            bit_depth=4,
            rgb_pins=[
                board.MTX_R1,
                board.MTX_G1,
                board.MTX_B1,
                board.MTX_R2,
                board.MTX_G2,
                board.MTX_B2,
            ],
            addr_pins=[
                board.MTX_ADDRA,
                board.MTX_ADDRB,
                board.MTX_ADDRC,
                board.MTX_ADDRD,
            ],
            clock_pin=board.MTX_CLK,
            latch_pin=board.MTX_LAT,
            output_enable_pin=board.MTX_OE,
        )

        self.display = framebufferio.FramebufferDisplay(
            self.matrix,
            auto_refresh=True,
        )

        # Set the default LED matrix state

        self.group = displayio.Group()
        self.display.root_group = self.group

        self.mode = "blank"

        self.text = None
        self.text_color = 0xFFFFFF
        self.text_label = None

        self.brightness = 0.25

        self.animation = None

        self.scroll_x = WIDTH
        self.last_scroll = time.monotonic()

    # -----------------------------
    # Color utilities
    # -----------------------------

    def _apply_brightness(self, color):
        
        # Scale an RGB color by brightness

        red = (color >> 16) & 0xFF
        green = (color >> 8) & 0xFF
        blue = color & 0xFF

        red = int(red * self.brightness)
        green = int(green * self.brightness)
        blue = int(blue * self.brightness)

        return (red << 16) | (green << 8) | blue

    # -----------------------------
    # Clear display
    # -----------------------------

    def _clear_group(self):
        
        # Remove everything from the display group

        while len(self.group) > 0:
            self.group.pop()

        self.text_label = None

    def clear(self):
        
        # Stop the active mode and clear the LEDs

        self.mode = "blank"

        self.text = None
        self.animation = None

        self._clear_group()

    # -----------------------------
    # Scrolling text
    # -----------------------------

    def set_text(self, text, color):
        
        # Start displaying scrolling text

        self._clear_group()

        self.mode = "text"

        self.text = text
        self.text_color = color
        self.animation = None

        # Apply brightness to the requested color
        display_color = self._apply_brightness(color)

        # Create the text label
        self.text_label = label.Label(
            terminalio.FONT,
            text=text,
            color=display_color,
        )

        # Anchor left edge at vertical center
        self.text_label.anchor_point = (0.0, 0.5)

        # Start outside the right side of matrix
        self.scroll_x = WIDTH

        self.text_label.anchored_position = (
            self.scroll_x,
            HEIGHT // 2,
        )

        self.group.append(self.text_label)
        self.last_scroll = time.monotonic()

    def _update_text(self):
        
        # Move the text left by one pixel when due

        if self.text_label is None:
            return

        now = time.monotonic()

        if now - self.last_scroll < SCROLL_INTERVAL:
            return

        self.last_scroll = now

        # Move text one pixel left
        self.scroll_x -= 1

        # Get total text width
        text_width = self.text_label.bounding_box[2]

        # Restart once text has left the screen
        if self.scroll_x < -text_width:
            self.scroll_x = WIDTH

        self.text_label.anchored_position = (
            self.scroll_x,
            HEIGHT // 2,
        )

    # -----------------------------
    # Brightness
    # -----------------------------

    def set_brightness(self, brightness):
        
        # Update brightness without restarting text

        self.brightness = max(
            0.0,
            min(1.0, brightness),
        )

        if self.text_label is not None:
            self.text_label.color = self._apply_brightness(
                self.text_color
            )

    # -----------------------------
    # Animations
    # -----------------------------

    def set_animation(self, animation):
        
        # Select an animation mode 

        self._clear_group()

        self.mode = "animation"
        self.animation = animation
        self.text = None

        # TODO: Render animation frames

    # -----------------------------
    # Main update function
    # -----------------------------

    def update(self):
        
        # Advance the active display mode for both text and animation

        if self.mode == "text":
            self._update_text()

        elif self.mode == "animation":
            # TODO: Update animation frames
            pass
