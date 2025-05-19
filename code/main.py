from settings import *
from player import Player

class Game:
    def __init__(self):
        # setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Top Down Shooter')
        self.clock = pygame.time.Clock()
        self.running = True

        # groups
        self.all_sprites = pygame.sprite.Group()

        # sprites
        self.player = Player((400,300), self.all_sprites)
    
    def run(self):
        while self.running:
            # dt
            dt = self.clock.tick() / 1000

            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            # update
            self.all_sprites.update(dt)
            # draw
            self.all_sprites.draw(self.display_surface)
            pygame.display.update()

        pygame.quit()

if __name__ == "__main__":    
    game = Game()
    game.run()
