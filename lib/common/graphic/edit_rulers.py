import pygame

def draw_ruler(screen, screen_objects, ruler_color, selected_ruler_color):
    screen_width, screen_height = screen.get_size()
    screen_center = (screen_width // 2, screen_height // 2)

    # Draw center lines of the screen
    draw_dashed_line(screen, ruler_color, (screen_center[0], 0), (screen_center[0], screen_height))
    draw_dashed_line(screen, ruler_color, (0, screen_center[1]), (screen_width, screen_center[1]))

    font = pygame.font.Font(None, 24)

    selected_objects = [obj for obj in screen_objects if obj.selected]
    
    if not selected_objects:
        return

    threshold = 5  # Proximity threshold for showing rulers
    align_threshold = 1  # Threshold for considering objects aligned

    for selected_obj in selected_objects:
        aligned_edges = get_aligned_edges(selected_obj, screen_objects, align_threshold)
        draw_object_rulers(screen, selected_obj, selected_ruler_color, font, aligned_edges)

        for obj in screen_objects:
            if obj.type == 'module' and obj.module is None:
                continue
            if obj.selected:
                continue

            if is_close_to_selected(selected_obj, obj, threshold):
                obj_aligned_edges = get_aligned_edges(obj, [selected_obj], align_threshold)
                draw_object_rulers(screen, obj, ruler_color, font, obj_aligned_edges)

def get_aligned_edges(selected_obj, screen_objects, threshold):
    aligned_edges = {
        'left': False, 'right': False, 'top': False, 'bottom': False,
        'center_x': False, 'center_y': False
    }
    
    for obj in screen_objects:
        if obj == selected_obj or (obj.type == 'module' and obj.module is None):
            continue
        
        if abs(selected_obj.x - obj.x) < threshold:
            aligned_edges['left'] = True
        if abs((selected_obj.x + selected_obj.width) - (obj.x + obj.width)) < threshold:
            aligned_edges['right'] = True
        if abs(selected_obj.y - obj.y) < threshold:
            aligned_edges['top'] = True
        if abs((selected_obj.y + selected_obj.height) - (obj.y + obj.height)) < threshold:
            aligned_edges['bottom'] = True
        
        selected_center_x = selected_obj.x + selected_obj.width // 2
        selected_center_y = selected_obj.y + selected_obj.height // 2
        obj_center_x = obj.x + obj.width // 2
        obj_center_y = obj.y + obj.height // 2
        
        if abs(selected_center_x - obj_center_x) < threshold:
            aligned_edges['center_x'] = True
        if abs(selected_center_y - obj_center_y) < threshold:
            aligned_edges['center_y'] = True
    
    return aligned_edges

def draw_object_rulers(screen, obj, color, font, aligned_edges):
    screen_width, screen_height = screen.get_size()
    obj_center = (obj.x + obj.width // 2, obj.y + obj.height // 2)
    
    magenta = (255, 0, 255)
    
    # Draw small plus at the center of the object
    plus_size = 30
    pygame.draw.line(screen, color, (obj_center[0] - plus_size, obj_center[1]), (obj_center[0] + plus_size, obj_center[1]))
    pygame.draw.line(screen, color, (obj_center[0], obj_center[1] - plus_size), (obj_center[0], obj_center[1] + plus_size))

    if obj.selected:
        # Draw all ruler lines for selected objects
        # Draw vertical center line
        center_x_color = magenta if aligned_edges['center_x'] else color
        draw_dashed_line(screen, center_x_color, (obj_center[0], 0), (obj_center[0], screen_height))

        # Draw horizontal center line
        center_y_color = magenta if aligned_edges['center_y'] else color
        draw_dashed_line(screen, center_y_color, (0, obj_center[1]), (screen_width, obj_center[1]))

        # Draw left vertical line
        left_color = magenta if aligned_edges['left'] else color
        draw_dashed_line(screen, left_color, (obj.x, 0), (obj.x, screen_height))

        # Draw right vertical line
        right_color = magenta if aligned_edges['right'] else color
        draw_dashed_line(screen, right_color, (obj.x + obj.width, 0), (obj.x + obj.width, screen_height))

        # Draw top horizontal line
        top_color = magenta if aligned_edges['top'] else color
        draw_dashed_line(screen, top_color, (0, obj.y), (screen_width, obj.y))

        # Draw bottom horizontal line
        bottom_color = magenta if aligned_edges['bottom'] else color
        draw_dashed_line(screen, bottom_color, (0, obj.y + obj.height), (screen_width, obj.y + obj.height))

        # Draw position (x, y) in the top-left corner
        pos_text = f"({obj.x}, {obj.y})"
        pos_surface = font.render(pos_text, True, color)
        screen.blit(pos_surface, (obj.x + 5, obj.y + 5))

        # Draw width at the bottom
        width_text = f"W: {obj.width}"
        width_surface = font.render(width_text, True, color)
        width_rect = width_surface.get_rect(center=(obj.x + obj.width // 2, obj.y + obj.height - 15))
        screen.blit(width_surface, width_rect)

        # Draw height on the right side
        height_text = f"H: {obj.height}"
        height_surface = font.render(height_text, True, color)
        height_surface = pygame.transform.rotate(height_surface, 90)
        height_rect = height_surface.get_rect(center=(obj.x + obj.width - 15, obj.y + obj.height // 2))
        screen.blit(height_surface, height_rect)
    else:
        # For non-selected objects, only draw aligned lines
        if aligned_edges['center_x']:
            draw_dashed_line(screen, magenta, (obj_center[0], 0), (obj_center[0], screen_height))
            # hightlight the whole object
            pygame.draw.rect(screen, magenta, (obj.x, obj.y, obj.width, obj.height), 2)
        if aligned_edges['center_y']:
            draw_dashed_line(screen, magenta, (0, obj_center[1]), (screen_width, obj_center[1]))
            # hightlight the whole object
            pygame.draw.rect(screen, magenta, (obj.x, obj.y, obj.width, obj.height), 2)
        if aligned_edges['left']:
            draw_dashed_line(screen, magenta, (obj.x, 0), (obj.x, screen_height))
            # hightlight the left line of the object
            pygame.draw.line(screen, magenta, (obj.x, obj.y), (obj.x, obj.y + obj.height), 2)
        if aligned_edges['right']:
            draw_dashed_line(screen, magenta, (obj.x + obj.width, 0), (obj.x + obj.width, screen_height))
            # hightlight the right line of the object
            pygame.draw.line(screen, magenta, (obj.x + obj.width, obj.y), (obj.x + obj.width, obj.y + obj.height), 2)
        if aligned_edges['top']:
            draw_dashed_line(screen, magenta, (0, obj.y), (screen_width, obj.y))
            # hightlight the top line of the object.
            pygame.draw.rect(screen, magenta, (obj.x, obj.y, obj.width, 2), 2)
        if aligned_edges['bottom']:
            draw_dashed_line(screen, magenta, (0, obj.y + obj.height), (screen_width, obj.y + obj.height))
            # hightlight the bottom line of the object.
            pygame.draw.line(screen, magenta, (obj.x, obj.y + obj.height), (obj.x + obj.width, obj.y + obj.height), 2)

def is_close_to_selected(selected_obj, obj, threshold):
    # Check horizontal lines
    if (abs(selected_obj.y - obj.y) < threshold or
        abs(selected_obj.y - (obj.y + obj.height)) < threshold or
        abs((selected_obj.y + selected_obj.height) - obj.y) < threshold or
        abs((selected_obj.y + selected_obj.height) - (obj.y + obj.height)) < threshold):
        return True

    # Check vertical lines
    if (abs(selected_obj.x - obj.x) < threshold or
        abs(selected_obj.x - (obj.x + obj.width)) < threshold or
        abs((selected_obj.x + selected_obj.width) - obj.x) < threshold or
        abs((selected_obj.x + selected_obj.width) - (obj.x + obj.width)) < threshold):
        return True

    # Check center lines
    selected_center_x = selected_obj.x + selected_obj.width // 2
    selected_center_y = selected_obj.y + selected_obj.height // 2
    obj_center_x = obj.x + obj.width // 2
    obj_center_y = obj.y + obj.height // 2

    if abs(selected_center_x - obj_center_x) < threshold or abs(selected_center_y - obj_center_y) < threshold:
        return True

    return False

def draw_dashed_line(surface, color, start_pos, end_pos, dash_length=10):
    x1, y1 = start_pos
    x2, y2 = end_pos
    dx = x2 - x1
    dy = y2 - y1
    distance = max(abs(dx), abs(dy))
    if distance == 0:
        return
    dx = dx / distance
    dy = dy / distance

    for i in range(0, int(distance), dash_length * 2):
        start = (int(x1 + i * dx), int(y1 + i * dy))
        end = (int(x1 + (i + dash_length) * dx), int(y1 + (i + dash_length) * dy))
        pygame.draw.line(surface, color, start, end, 1)
