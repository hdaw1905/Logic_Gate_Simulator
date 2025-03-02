import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 1000, 600  # Increased width to accommodate the sidebar
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Logic Gate Simulator")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
LIGHT_GRAY = (220, 220, 220)

COLORS = [RED, GREEN, BLUE]  # List of colors for wires

# Font for text
font = pygame.font.Font(None, 24)

# Sidebar settings
SIDEBAR_WIDTH = 200
COMPONENT_BUTTON_HEIGHT = 40
COMPONENT_TYPES = ["AND", "OR", "NOT", "NAND", "NOR", "XOR", "XNOR", "Switch", "LED"]


# LogicGate class
class LogicGate:
    def __init__(self, x, y, gate_type):
        self.x = x
        self.y = y
        self.gate_type = gate_type
        self.color = BLUE
        self.width = 60
        self.height = 40
        self.state = False  # Current output state
        self.update_positions()  # Initialize positions

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        text = font.render(self.gate_type, True, WHITE)
        screen.blit(text, (self.x + 5, self.y + 10))

        # Draw input slots
        for input_pos in self.inputs:
            pygame.draw.circle(screen, BLACK, input_pos, 5)

        # Draw output slot
        pygame.draw.circle(screen, BLACK, self.output, 5)

    def update_positions(self):
        # Update slot positions based on the current position of the gate
        self.inputs = [(self.x - 10, self.y + 10), (self.x - 10, self.y + 30)]
        if self.gate_type == "NOT":  # NOT gate has only one input
            self.inputs = [(self.x - 10, self.y + 20)]
        self.output = (self.x + self.width + 10, self.y + self.height // 2)

    def calculate_output(self, inputs):
        """Calculate the output of the given gate based on its type and input states."""
        if self.gate_type == "AND":
            # AND gate: Output is 1 only if all inputs are 1
            self.state = all(inputs)
        elif self.gate_type == "OR":
            # OR gate: Output is 1 if at least one input is 1
            self.state = any(inputs)
        elif self.gate_type == "NOT":
            # NOT gate: Output is the inverse of the single input
            if len(inputs) > 0:
                self.state = not inputs[0]
            else:
                self.state = False  # Default state if no inputs
        elif self.gate_type == "NAND":
            # NAND gate: Output is 0 only if all inputs are 1
            self.state = not all(inputs)
        elif self.gate_type == "NOR":
            # NOR gate: Output is 1 only if all inputs are 0
            self.state = not any(inputs)
        elif self.gate_type == "XOR":
            # XOR gate: Output is 1 if the number of inputs with state 1 is odd
            if len(inputs) == 2:
                self.state = inputs[0] != inputs[1]
            else:
                self.state = False  # Default if not exactly two inputs
        elif self.gate_type == "XNOR":
            # XNOR gate: Output is 1 if the number of inputs with state 1 is even
            if len(inputs) == 2:
                self.state = inputs[0] == inputs[1]
            else:
                self.state = False  # Default if not exactly two inputs
        return self.state  # Return the current output state

    def is_clicked(self, pos):
        return self.x < pos[0] < self.x + self.width and self.y < pos[1] < self.y + self.height

    def get_slot_clicked(self, pos):
        for input_pos in self.inputs:
            if (pos[0] - input_pos[0]) ** 2 + (pos[1] - input_pos[1]) ** 2 < 25:
                return input_pos
        if (pos[0] - self.output[0]) ** 2 + (pos[1] - self.output[1]) ** 2 < 25:
            return self.output
        return None


# Switch class
class Switch:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 20
        self.state = False  # OFF by default
        self.update_positions()  # Initialize output slot position

    def toggle(self):
        self.state = not self.state

    def draw(self, screen):
        pygame.draw.rect(screen, GRAY, (self.x, self.y, self.width, self.height))
        if self.state:
            pygame.draw.circle(screen, GREEN, (self.x + self.width - 10, self.y + self.height // 2), 8)
        else:
            pygame.draw.circle(screen, RED, (self.x + 10, self.y + self.height // 2), 8)
        pygame.draw.circle(screen, BLACK, self.output, 5)

    def update_positions(self):
        self.output = (self.x + self.width + 10, self.y + self.height // 2)

    def is_clicked(self, pos):
        return self.x < pos[0] < self.x + self.width and self.y < pos[1] < self.y + self.height

    def get_slot_clicked(self, pos):
        if (pos[0] - self.output[0]) ** 2 + (pos[1] - self.output[1]) ** 2 < 25:
            return self.output
        return None


# LED class
class LED:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.state = False  # OFF by default
        self.update_positions()  # Initialize input slot position

    def draw(self, screen):
        color = GREEN if self.state else RED  # Change color based on state
        pygame.draw.ellipse(screen, color, (self.x, self.y, self.width, self.height))
        pygame.draw.circle(screen, BLACK, self.inputs[0], 5)

    def update_positions(self):
        self.inputs = [(self.x - 10, self.y + self.height // 2)]

    def is_clicked(self, pos):
        return self.x < pos[0] < self.x + self.width and self.y < pos[1] < self.y + self.height

    def get_slot_clicked(self, pos):
        if (pos[0] - self.inputs[0][0]) ** 2 + (pos[1] - self.inputs[0][1]) ** 2 < 25:
            return self.inputs[0]
        return None


# Wire class
class Wire:
    def __init__(self, start_gate, start_slot, end_gate, end_slot, color):
        self.start_gate = start_gate
        self.start_slot = start_slot
        self.end_gate = end_gate
        self.end_slot = end_slot
        self.color = color

    def draw(self, screen):
        start_pos = self.get_start_position()
        end_pos = self.get_end_position()

        # Draw the wire only if both positions are valid
        if start_pos and end_pos:
            pygame.draw.line(screen, self.color, start_pos, end_pos, 3)

    def get_start_position(self):
        # Determine start position based on the current state of the start gate
        if hasattr(self.start_gate, "output") and self.start_slot == self.start_gate.output:
            return self.start_gate.output
        elif hasattr(self.start_gate, "inputs") and self.start_slot in self.start_gate.inputs:
            return self.start_slot
        return None

    def get_end_position(self):
        # Determine end position based on the current state of the end gate
        if hasattr(self.end_gate, "output") and self.end_slot == self.end_gate.output:
            return self.end_gate.output
        elif hasattr(self.end_gate, "inputs") and self.end_slot in self.end_gate.inputs:
            return self.end_slot
        return None

    def is_clicked(self, pos):
        start_pos = self.get_start_position()
        end_pos = self.get_end_position()

        if start_pos and end_pos:
            line_length = ((end_pos[0] - start_pos[0]) ** 2 + (end_pos[1] - start_pos[1]) ** 2) ** 0.5
            if line_length == 0:
                return False

            # Calculate projection factor
            t = ((pos[0] - start_pos[0]) * (end_pos[0] - start_pos[0]) +
                 (pos[1] - start_pos[1]) * (end_pos[1] - start_pos[1])) / (line_length ** 2)
            t = max(0, min(1, t))  # Clamp to [0,1]
            projection = (
            start_pos[0] + t * (end_pos[0] - start_pos[0]), start_pos[1] + t * (end_pos[1] - start_pos[1]))

            distance = ((projection[0] - pos[0]) ** 2 + (projection[1] - pos[1]) ** 2) ** 0.5
            return distance < 5  # Click sensitivity threshold

        return False


# Initialize gates, switches, LEDs, and wires
gates = []
switches = []
leds = []
wires = []
current_wire = None
selected_component = None  # Track the selected component from the sidebar


# Function to draw the sidebar
def draw_sidebar():
    pygame.draw.rect(screen, LIGHT_GRAY, (0, 0, SIDEBAR_WIDTH, HEIGHT))
    for i, component in enumerate(COMPONENT_TYPES):
        button_rect = pygame.Rect(10, 10 + i * (COMPONENT_BUTTON_HEIGHT + 10), SIDEBAR_WIDTH - 20, COMPONENT_BUTTON_HEIGHT)
        pygame.draw.rect(screen, GRAY, button_rect)
        text = font.render(component, True, BLACK)
        screen.blit(text, (button_rect.x + 10, button_rect.y + 10))


# Main loop
running = True
dragging_component = None

while running:
    screen.fill(WHITE)

    # Draw the sidebar
    draw_sidebar()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check if a sidebar button is clicked
                if event.pos[0] < SIDEBAR_WIDTH:
                    for i, component in enumerate(COMPONENT_TYPES):
                        button_rect = pygame.Rect(10, 10 + i * (COMPONENT_BUTTON_HEIGHT + 10), SIDEBAR_WIDTH - 20, COMPONENT_BUTTON_HEIGHT)
                        if button_rect.collidepoint(event.pos):
                            selected_component = component  # Set the selected component
                            break

                # Toggle switches
                for switch in switches:
                    if switch.is_clicked(event.pos):
                        switch.toggle()

                # Check if a component is clicked
                for component in gates + switches + leds:
                    if component.is_clicked(event.pos):
                        dragging_component = component

                # Check if a slot is clicked for wire creation
                for component in gates + switches + leds:
                    slot = component.get_slot_clicked(event.pos) if hasattr(component, "get_slot_clicked") else None
                    if slot:
                        if current_wire is None:
                            current_wire = [component, slot]  # Start wire
                        else:
                            start_gate, start_slot = current_wire
                            end_gate, end_slot = component, slot
                            wires.append(
                                Wire(start_gate, start_slot, end_gate, end_slot, random.choice(COLORS)))  # Create wire
                            current_wire = None  # Reset wire

                # Place the selected component in the environment
                if selected_component and event.pos[0] > SIDEBAR_WIDTH:
                    if selected_component in ["AND", "OR", "NOT", "NAND", "NOR", "XOR", "XNOR"]:
                        gates.append(LogicGate(event.pos[0], event.pos[1], selected_component))
                    elif selected_component == "Switch":
                        switches.append(Switch(event.pos[0], event.pos[1]))
                    elif selected_component == "LED":
                        leds.append(LED(event.pos[0], event.pos[1]))
                    selected_component = None  # Reset selection

            elif event.button == 3:  # Right click
                if current_wire:
                    current_wire = None  # Cancel wire creation
                else:
                    # Delete wire on right-click
                    for wire in wires:
                        if wire.is_clicked(event.pos):
                            wires.remove(wire)
                            break

        elif event.type == pygame.MOUSEBUTTONUP:
            dragging_component = None  # Stop dragging

        elif event.type == pygame.MOUSEMOTION:
            if dragging_component:
                # Update position of the dragging component
                dragging_component.x, dragging_component.y = event.pos
                dragging_component.update_positions()  # Update the position of the component's slots

    # Gather the state of each logic gate based on the connections
    for gate in gates:
        inputs = []
        for wire in wires:
            if wire.end_gate == gate:
                # Collect input states from connected wires
                # Check if the source component is a Switch
                if isinstance(wire.start_gate, Switch):
                    inputs.append(wire.start_gate.state)
                # If it's a gate, use the last calculated state.
                elif isinstance(wire.start_gate, LogicGate):
                    inputs.append(wire.start_gate.state)
                # LEDs typically won't provide state as they don’t generate input (only display output).
        gate.calculate_output(inputs)  # Calculate output for current gate

    # Update LED state based on the connected gate's output
    for led in leds:
        led.state = False  # Default to OFF
        for wire in wires:
            if wire.end_gate == led:  # Check if the LED is connected to a gate
                if isinstance(wire.start_gate, LogicGate):
                    led.state = wire.start_gate.state  # Set LED state to the connected gate's output

    # Draw components
    for gate in gates:
        gate.draw(screen)
    for switch in switches:
        switch.draw(screen)
    for led in leds:
        led.draw(screen)

    # Draw wires after drawing components to keep them behind the components
    for wire in wires:
        wire.draw(screen)

    # Draw the current wire being created
    if current_wire:
        pygame.draw.line(screen, BLACK, current_wire[1], pygame.mouse.get_pos(), 3)

    pygame.display.flip()

pygame.quit()
sys.exit()
