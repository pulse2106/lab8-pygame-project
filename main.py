import pygame
import random
import time

# method to show the list of height
def show(arr, win):
    width = 40
    for i in range(arr):
        x = random.randint(0, 500)
        y = random.randint(0, 400)
        if i % 2 == 0:
            pygame.draw.rect(win, (255, 0, 0), (x, y, width, (arr)))
        else:
            pygame.draw.rect(win, (0, 255, 0), (x, y, width, (arr)))


# infinite loop
def main():
    pygame.init()
    # setting window size
    win = pygame.display.set_mode((500, 400))
    # setting title to the window
    pygame.display.set_caption("Bubble sort")
    run = True
    arr = 10
    while run:
        # execute flag to start sorting
        execute = False
        # time delay
        pygame.time.delay(10)
        # getting keys pressed
        keys = pygame.key.get_pressed()
        # iterating events
        for event in pygame.event.get():
            # if event is to quit
            if event.type == pygame.QUIT:
                # making run = false so break the while loop
                run = False
        # checking if execute flag is false
        if execute == False:
            # fill the window with black color
            win.fill((0, 0, 0))
            # call the height method to show the list items
            show(arr, win)
            # update the window
            pygame.display.update()
            time.sleep(1.0)
            run == False

# exiting the main window
pygame.quit()

# sourced from https://www.geeksforgeeks.org/python/bubble-sort-visualizer-using-pygame/

if __name__ == "__main__":
    main()