import pygame


def scale_image(img, factor):                                                   # function that enable us to scale the image
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pygame.transform.scale(img, size)


def blit_rotate_center(win, image, top_left, angle):                            # this function enable us to rotate te car 
    rotated_image = pygame.transform.rotate(image, angle)                       # rotate the car/image      
    new_rect = rotated_image.get_rect(
        center=image.get_rect(topleft=top_left).center)                         # rotate the image from the center not from the topleft corner
    win.blit(rotated_image, new_rect.topleft)                                   # define the new x and y position such that it will be at the same position however it is rotate


def blit_text_center(win, font, text):                                          # use to load the text with the font that has been applied
    render = font.render(text, 1, (200, 200, 200))                              # set the color of the text
    win.blit(render, (win.get_width()/2 - render.get_width() /
                      2, win.get_height()/2 - render.get_height()/2))           # set the position of the text where the computer has to render it
