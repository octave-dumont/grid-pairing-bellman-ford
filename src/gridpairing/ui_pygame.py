import sys
import pygame
from pygame import gfxdraw

from .grid import Grid
from .solvers import SolverBellmanFord

# Pygame initialization
pygame.init()

# Color configuration
BACKGROUND = (30, 30, 40)
GRID_LINES = (70, 70, 80)
BUTTON_COLOR = (80, 120, 170)
BUTTON_HOVER = (100, 140, 200)
TEXT_COLOR = (220, 220, 220)
HIGHLIGHT_COLOR = (255, 230, 100, 180)  # Semi-transparent yellow
LINE_COLOR = (255, 200, 40)

# Improved graphic/layout configuration
CELL_SIZE = 60
MARGIN = 3
BUTTON_HEIGHT = 40
SIDEBAR_WIDTH = 200
ANIMATION_SPEED = 10  # Animation speed

# Modern color palette
COLOR_MAP = {
    0: (240, 240, 240),  # White
    1: (231, 76, 60),    # Red
    2: (52, 152, 219),   # Blue
    3: (46, 204, 113),   # Green
    4: (44, 62, 80)      # Black
}

# Improved fonts
FONT_PATH = pygame.font.get_default_font()
FONT = pygame.font.Font(FONT_PATH, 16)
FONT_LARGE = pygame.font.Font(FONT_PATH, 24)
FONT_SMALL = pygame.font.Font(FONT_PATH, 14)

# Load grid
try:
    grid = Grid.grid_from_file("input/grid05.in")
except FileNotFoundError:
    print("Error: grid file not found.")
    available_files = ["grid01.in", "grid02.in", "grid03.in", "grid04.in", "grid05.in"]
    print(f"Try one of these files: {', '.join(available_files)}")
    sys.exit(1)

solver = SolverBellmanFord(grid)

# Window dimensions
WIDTH = grid.m * (CELL_SIZE + MARGIN) + MARGIN + SIDEBAR_WIDTH
HEIGHT = max(grid.n * (CELL_SIZE + MARGIN) + MARGIN + BUTTON_HEIGHT * 3, 500)

# Create window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Interactive Grid (ENSAE Project 2025)")
icon = pygame.Surface((32, 32))
icon.fill((52, 152, 219))
pygame.display.set_icon(icon)

# State variables
selected_cells = []
user_pairs = []
hovering_cell = None
animation_progress = {}  # For line animations
buttons = []
show_solution = False
solution_pairs = []
show_help = False
last_score = 0
score_animation = {"target": 0, "current": 0}
best_score = None  # To store the best possible score

# Function to draw a rounded rectangle
def draw_rounded_rect(surface, rect, color, corner_radius):
    """Draw a rectangle with rounded corners."""
    if corner_radius < 0:
        corner_radius = 0
    
    # Limit corner radius to half the width/height
    corner_radius = min(corner_radius, rect.width // 2, rect.height // 2)
    
    # Fill rounded corners
    x, y, width, height = rect
    
    # Draw rounded corners
    gfxdraw.aacircle(surface, x + corner_radius, y + corner_radius, corner_radius, color)
    gfxdraw.filled_circle(surface, x + corner_radius, y + corner_radius, corner_radius, color)
    
    gfxdraw.aacircle(surface, x + width - corner_radius - 1, y + corner_radius, corner_radius, color)
    gfxdraw.filled_circle(surface, x + width - corner_radius - 1, y + corner_radius, corner_radius, color)
    
    gfxdraw.aacircle(surface, x + corner_radius, y + height - corner_radius - 1, corner_radius, color)
    gfxdraw.filled_circle(surface, x + corner_radius, y + height - corner_radius - 1, corner_radius, color)
    
    gfxdraw.aacircle(surface, x + width - corner_radius - 1, y + height - corner_radius - 1, corner_radius, color)
    gfxdraw.filled_circle(surface, x + width - corner_radius - 1, y + height - corner_radius - 1, corner_radius, color)
    
    # Fill remaining rectangles
    pygame.draw.rect(surface, color, (x + corner_radius, y, width - 2 * corner_radius, height))
    pygame.draw.rect(surface, color, (x, y + corner_radius, width, height - 2 * corner_radius))

# Button class
class Button:
    def __init__(self, rect, text, action, color=BUTTON_COLOR, hover_color=BUTTON_HOVER):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.action = action
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
    
    def draw(self):
        # Draw button background
        current_color = self.hover_color if self.is_hovered else self.color
        draw_rounded_rect(screen, self.rect, current_color, 8)
        
        # Add a subtle shadow effect
        if not self.is_hovered:
            shadow_rect = self.rect.copy()
            shadow_rect.y += 2
            draw_rounded_rect(screen, shadow_rect, (20, 20, 20, 100), 8)
        
        # Draw button text
        text_surf = FONT.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_hovered:
            self.action()
            return True
        return False

# Create buttons
def create_buttons():
    buttons = []
    
    # Determine available space
    grid_width = grid.m * (CELL_SIZE + MARGIN) + MARGIN
    button_width = min(200, grid_width - 20)
    button_x = grid_width + (SIDEBAR_WIDTH - button_width) // 2
    button_y_start = 20
    button_spacing = BUTTON_HEIGHT + 10
    
    # Add buttons
    buttons.append(Button(
        (button_x, button_y_start, button_width, BUTTON_HEIGHT),
        "Auto Solve", 
        auto_solve
    ))
    
    buttons.append(Button(
        (button_x, button_y_start + button_spacing, button_width, BUTTON_HEIGHT),
        "Reset", 
        reset_game
    ))
    
    buttons.append(Button(
        (button_x, button_y_start + button_spacing * 2, button_width, BUTTON_HEIGHT),
        "Help", 
        toggle_help
    ))
    
    buttons.append(Button(
        (button_x, button_y_start + button_spacing * 3, button_width, BUTTON_HEIGHT),
        "Quit", 
        lambda: pygame.event.post(pygame.event.Event(pygame.QUIT))
    ))
    
    return buttons

# Button actions
def auto_solve():
    global show_solution, solution_pairs, selected_cells, best_score
    selected_cells = []
    
    # Solve in the background
    solver.run()
    solution_pairs = solver.pairs.copy()
    
    # Compute the best possible score
    best_score = calculate_score(solution_pairs)
    
    # Toggle solution display
    show_solution = not show_solution
    
    # Reset animations
    global animation_progress
    animation_progress = {}
    
    # Update button text
    buttons[0].text = "Hide Solution" if show_solution else "Auto Solve"

def reset_game():
    global user_pairs, selected_cells, show_solution
    user_pairs = []
    selected_cells = []
    show_solution = False
    animation_progress.clear()
    buttons[0].text = "Auto Solve"

def toggle_help():
    global show_help
    show_help = not show_help

# Functions to draw UI elements
def draw_cell(i, j, highlight=False):
    # Cell position and dimensions
    x = j * (CELL_SIZE + MARGIN) + MARGIN
    y = i * (CELL_SIZE + MARGIN) + MARGIN
    rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
    
    # Base cell color
    color = COLOR_MAP[grid.color[i][j]]
    
    # Draw cell with slightly rounded corners
    draw_rounded_rect(screen, rect, color, 4)
    
    # Add depth/shadow effect
    if grid.color[i][j] != 4:  # No shadow for black cells
        pygame.draw.line(
            screen,
            (color[0] * 0.8, color[1] * 0.8, color[2] * 0.8),
            (x, y + CELL_SIZE),
            (x + CELL_SIZE, y + CELL_SIZE),
            2
        )
        pygame.draw.line(
            screen,
            (color[0] * 0.8, color[1] * 0.8, color[2] * 0.8),
            (x + CELL_SIZE, y),
            (x + CELL_SIZE, y + CELL_SIZE),
            2
        )
    
    # Highlight cell if needed
    if highlight:
        highlight_rect = rect.inflate(-4, -4)
        pygame.draw.rect(screen, HIGHLIGHT_COLOR, highlight_rect, 3, border_radius=3)
    
    # Display value
    if not grid.is_forbidden(i, j):
        text_color = (255, 255, 255) if grid.color[i][j] in [2, 4] else (0, 0, 0)
        text = FONT.render(str(grid.value[i][j]), True, text_color)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)

def draw_pair_line(cell1, cell2, progress=1.0, color=LINE_COLOR, width=3):
    x1, y1 = cell1
    x2, y2 = cell2
    
    # Center positions of cells
    start_x = y1 * (CELL_SIZE + MARGIN) + CELL_SIZE // 2 + MARGIN
    start_y = x1 * (CELL_SIZE + MARGIN) + CELL_SIZE // 2 + MARGIN
    end_x = y2 * (CELL_SIZE + MARGIN) + CELL_SIZE // 2 + MARGIN
    end_y = x2 * (CELL_SIZE + MARGIN) + CELL_SIZE // 2 + MARGIN
    
    # If animation is in progress, compute current end position
    if progress < 1.0:
        current_x = start_x + (end_x - start_x) * progress
        current_y = start_y + (end_y - start_y) * progress
        end_x, end_y = current_x, current_y
    
    # Draw anti-aliased line
    gfxdraw.line(screen, int(start_x), int(start_y), int(end_x), int(end_y), color)
    
    # Thicken the line by drawing several lines
    for i in range(1, width):
        offset = i // 2
        if i % 2 == 0:
            gfxdraw.line(
                screen,
                int(start_x + offset),
                int(start_y),
                int(end_x + offset),
                int(end_y),
                color
            )
        else:
            gfxdraw.line(
                screen,
                int(start_x),
                int(start_y + offset),
                int(end_x),
                int(end_y + offset),
                color
            )

def draw_sidebar():
    # Sidebar background
    sidebar_rect = pygame.Rect(grid.m * (CELL_SIZE + MARGIN) + MARGIN, 0, SIDEBAR_WIDTH, HEIGHT)
    pygame.draw.rect(screen, (40, 40, 50), sidebar_rect)
    pygame.draw.line(screen, GRID_LINES, (sidebar_rect.x, 0), (sidebar_rect.x, HEIGHT), 2)
    
    # Draw buttons
    for button in buttons:
        button.draw()
    
    # Display score with animation
    score_text = FONT_LARGE.render(f"Score: {int(score_animation['current'])}", True, TEXT_COLOR)
    score_rect = score_text.get_rect(topleft=(sidebar_rect.x + 20, HEIGHT - 140))
    screen.blit(score_text, score_rect)
    
    # Display best possible score if available
    if best_score is not None:
        best_score_text = FONT.render(f"Best score: {best_score}", True, (150, 255, 150))
        best_score_rect = best_score_text.get_rect(topleft=(sidebar_rect.x + 20, HEIGHT - 110))
        screen.blit(best_score_text, best_score_rect)
    
    # Display grid info
    grid_info = FONT_SMALL.render(f"Grid: {grid.n}×{grid.m}", True, TEXT_COLOR)
    screen.blit(grid_info, (sidebar_rect.x + 20, HEIGHT - 60))

def draw_help_overlay():
    if not show_help:
        return
    
    # Semi-transparent background
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    # Help box
    help_width = 500
    help_height = 300
    help_rect = pygame.Rect((WIDTH - help_width) // 2, (HEIGHT - help_height) // 2, help_width, help_height)
    draw_rounded_rect(screen, help_rect, (50, 50, 60), 10)
    
    # Title
    title = FONT_LARGE.render("How to play", True, TEXT_COLOR)
    title_rect = title.get_rect(midtop=(help_rect.centerx, help_rect.y + 20))
    screen.blit(title, title_rect)
    
    # Instructions
    instructions = [
        "• Click two compatible cells to create a pair",
        "• Create pairs to improve your score",
        "• Unmatched cells add their value to the score",
        "• Pairs add their cost to the score",
        "• Press Space to auto-solve",
        "• Click an existing pair to delete it",
        "• Press H to show/hide this help"
    ]
    
    for i, line in enumerate(instructions):
        text = FONT.render(line, True, TEXT_COLOR)
        screen.blit(text, (help_rect.x + 30, help_rect.y + 70 + i * 30))
    
    # Close hint
    close_text = FONT.render("Click anywhere to close", True, (180, 180, 180))
    close_rect = close_text.get_rect(midbottom=(help_rect.centerx, help_rect.bottom - 20))
    screen.blit(close_text, close_rect)

def calculate_score(pairs):
    """Compute the total score."""
    score = 0
    
    # Add cost of pairs
    if pairs:
        score += sum(grid.cost(pair) for pair in pairs)
    
    # Find already paired cells
    paired_cells = {cell for pair in pairs for cell in pair} if pairs else set()
    
    # Add value of unpaired cells
    for i in range(grid.n):
        for j in range(grid.m):
            if (i, j) not in paired_cells and not grid.is_forbidden(i, j):
                score += grid.value[i][j]
    
    return score

def draw_grid():
    global last_score, hovering_cell
    
    # Update score animation
    target_score = calculate_score(user_pairs)
    if target_score != score_animation["target"]:
        score_animation["target"] = target_score
    
    # Smooth score animation
    score_diff = score_animation["target"] - score_animation["current"]
    if abs(score_diff) > 0.5:
        score_animation["current"] += score_diff * 0.1
    else:
        score_animation["current"] = score_animation["target"]
    
    # Draw background
    screen.fill(BACKGROUND)
    
    # Draw each cell
    for i in range(grid.n):
        for j in range(grid.m):
            # Determine if cell is selected or hovered
            is_selected = (i, j) in selected_cells
            is_hovered = hovering_cell == (i, j)
            draw_cell(i, j, highlight=is_selected or is_hovered)
    
    # Draw user pairs with animation
    for idx, (cell1, cell2) in enumerate(user_pairs):
        pair_key = f"user_{idx}"
        if pair_key not in animation_progress:
            animation_progress[pair_key] = 0.0
        
        # Update animation
        if animation_progress[pair_key] < 1.0:
            animation_progress[pair_key] += 0.05
        
        # Draw line
        draw_pair_line(cell1, cell2, animation_progress[pair_key], LINE_COLOR, width=4)
    
    # Draw solution if requested
    if show_solution:
        for idx, (cell1, cell2) in enumerate(solution_pairs):
            pair_key = f"solution_{idx}"
            if pair_key not in animation_progress:
                animation_progress[pair_key] = 0.0
            
            # Update animation with a slight delay for each pair
            if animation_progress[pair_key] < 1.0:
                animation_progress[pair_key] += 0.03
            
            # Draw solution line
            draw_pair_line(cell1, cell2, animation_progress[pair_key], (100, 200, 100, 180), width=2)
    
    # Draw sidebar
    draw_sidebar()
    
    # Draw help if needed
    draw_help_overlay()
    
    # Update display
    pygame.display.flip()

def handle_cell_click(pos):
    # Convert mouse position to cell coordinates
    j = pos[0] // (CELL_SIZE + MARGIN)
    i = pos[1] // (CELL_SIZE + MARGIN)
    
    # Check that the cell is valid
    if i >= grid.n or j >= grid.m or grid.is_forbidden(i, j):
        return
    
    global selected_cells, user_pairs
    
    # Check if we clicked on an existing pair
    for pair_idx, (c1, c2) in enumerate(user_pairs):
        if (i, j) in [c1, c2]:
            # Remove the pair
            user_pairs.pop(pair_idx)
            # Remove corresponding animation
            animation_progress.pop(f"user_{pair_idx}", None)
            # Reindex remaining animations
            new_animation_progress = {}
            for k, v in animation_progress.items():
                if k.startswith("user_"):
                    idx = int(k.split("_")[1])
                    if idx > pair_idx:
                        new_animation_progress[f"user_{idx-1}"] = v
                    else:
                        new_animation_progress[k] = v
                else:
                    new_animation_progress[k] = v
            animation_progress.clear()
            animation_progress.update(new_animation_progress)
            return
    
    # Handle selection
    if (i, j) in selected_cells:
        selected_cells.remove((i, j))
    else:
        selected_cells.append((i, j))
        # If we have two selected cells, try to form a pair
        if len(selected_cells) == 2:
            c1, c2 = selected_cells
            # Use test_pair to check if the pair is valid
            if grid.test_pair(c1, c2) and c1 != c2:
                # Check that cells are not already paired
                if all(c1 not in pair and c2 not in pair for pair in user_pairs):
                    user_pairs.append((c1, c2))
            selected_cells.clear()

def handle_mouse_motion(pos):
    global hovering_cell
    
    # Check if mouse is over the grid
    grid_width = grid.m * (CELL_SIZE + MARGIN) + MARGIN
    if pos[0] <= grid_width:
        # Convert position to cell coordinates
        j = pos[0] // (CELL_SIZE + MARGIN)
        i = pos[1] // (CELL_SIZE + MARGIN)
        
        # Update hovered cell
        if 0 <= i < grid.n and 0 <= j < grid.m and not grid.is_forbidden(i, j):
            hovering_cell = (i, j)
        else:
            hovering_cell = None
    else:
        hovering_cell = None
    
    # Update button hover state
    for button in buttons:
        button.check_hover(pos)

# Create buttons
buttons = create_buttons()

# Main loop
def main():
    global running
    running = True
    clock = pygame.time.Clock()
    
    # Show help at startup
    global show_help
    show_help = True
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # If help is displayed, close it on click
                if show_help:
                    show_help = False
                    continue
                
                # Check if a button was clicked
                button_clicked = False
                for button in buttons:
                    if button.handle_event(event):
                        button_clicked = True
                        break
                
                if not button_clicked:
                    handle_cell_click(pygame.mouse.get_pos())
            
            elif event.type == pygame.MOUSEMOTION:
                handle_mouse_motion(pygame.mouse.get_pos())
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    auto_solve()
                elif event.key == pygame.K_r:
                    reset_game()
                elif event.key == pygame.K_h:
                    toggle_help()
                elif event.key == pygame.K_ESCAPE:
                    running = False
        
        # Draw UI
        draw_grid()
        
        # Limit framerate
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
