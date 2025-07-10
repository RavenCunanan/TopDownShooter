from settings import *
from player import Player
from sprites import *
from pytmx.util_pygame import load_pygame
from random import randint, choice
from groups import AllSprites

class Game:
    def __init__(self):
        # setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Top Down Shooter')
        self.clock = pygame.time.Clock()
        self.running = True
        self.score = 0
        self.final_score = 0
        self.start_time = pygame.time.get_ticks()
        self.game_active = True
        
        # groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        # gun timer
        self.can_shoot = True
        self.shoot_time = 0
        self.gun_cooldown = 100 # milliseconds

        # enemy timer
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, 300)
        self.spawn_positions = []

        # audio
        self.shoot_sound = pygame.mixer.Sound(join('audio', 'shoot.wav'))
        self.shoot_sound.set_volume(0.2)
        self.impact_sound = pygame.mixer.Sound(join('audio', 'impact.ogg'))
        self.impact_sound.set_volume(0.4)
        self.music = pygame.mixer.Sound(join('audio', 'music.wav'))
        self.music.set_volume(0.2)
        self.music.play(loops=-1)
        
        # setup
        self.load_images()
        self.setup()

    def load_images(self):
        self.bullet_surf = pygame.image.load(join('images', 'gun', 'bullet.png')).convert_alpha()
        self.heart_image = pygame.image.load(join('images', 'ui', 'heart.png')).convert_alpha()

        folders = list(walk(join('images', 'enemies')))[0][1]
        self.enemy_frames = {}
        for folder in folders:
            for folder_path, _, file_names in walk(join('images', 'enemies', folder)):
                self.enemy_frames[folder] = []
                for file_name in sorted(file_names, key = lambda name: int(name.split('.')[0])):
                    full_path = join(folder_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.enemy_frames[folder].append(surf)
              
    def input(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            self.shoot_sound.play()
            pos = self.gun.rect.center + self.gun.player_direction * 50
            Bullet(self.bullet_surf,pos, self.gun.player_direction, (self.all_sprites, self.bullet_sprites))
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()
        
    def gun_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.gun_cooldown:
                self.can_shoot = True

    def setup(self):
        map = load_pygame('data\maps\world.tmx')

        for x,y, image in map.get_layer_by_name('Ground').tiles():
            Sprite((x * TILE_SIZE,y * TILE_SIZE), image, self.all_sprites)  
        
        for obj in map.get_layer_by_name('Objects'):
            CollisionSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))

        for obj in map.get_layer_by_name('Collisions'):
            CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)

        for obj in map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites)
                self.gun = Gun(self.player, self.all_sprites)
            else:
                self.spawn_positions.append((obj.x, obj.y))

    def player_collision(self):
       if pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask):
           self.player.take_damage()
           if not self.player.alive:
               current_time = pygame.time.get_ticks()
               time_elapsed = (current_time - self.start_time) // 1000
               self.final_score = time_elapsed + self.score
               self.game_active = False

    def bullet_collision(self):
        if self.bullet_sprites:
            for bullet in self.bullet_sprites:
                collision_sprites = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
                if collision_sprites:
                    self.impact_sound.play()
                    for sprite in collision_sprites:
                        sprite.destroy()
                        self.score += 5
                    bullet.kill()

    def run(self):
        while self.running:
            if self.game_active:
                self.run_gameplay()
            else:
                self.run_game_over()
        
        pygame.quit()
    
    def run_gameplay(self):
        dt = self.clock.tick() / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == self.enemy_event:
                Enemy(choice(self.spawn_positions), choice(list(self.enemy_frames.values())),
                    (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites)

        self.gun_timer()
        self.input()
        self.all_sprites.update(dt)
        self.bullet_collision()
        self.player_collision()

        current_time = pygame.time.get_ticks()
        time_elapsed = (current_time - self.start_time) // 1000
        total_score = time_elapsed + self.score

        self.display_surface.fill('black')
        self.all_sprites.draw(self.player.rect.center)

        font = pygame.font.Font(None, 36)
        score_surf = font.render(f'Score: {total_score}', True, 'white')
        self.display_surface.blit(score_surf, (10, 50))

        for i in range(self.player.health):
            x = 10 + i * (self.heart_image.get_width() + 5)
            self.display_surface.blit(self.heart_image, (x, 10))

        pygame.display.update()


    def run_game_over(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.restart_game()
        
        self.display_surface.fill('black')

        # main Game Over text
        font = pygame.font.Font(None, 64)
        game_over_text = font.render('Game Over', True, 'red')
        self.display_surface.blit(game_over_text, game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50)))

        #score text
        font_score = pygame.font.Font(None, 48)
        score_text = font_score.render(f'Final Score: {self.final_score}', True, 'white')
        self.display_surface.blit(score_text, score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)))

        # restart instruction
        font_small = pygame.font.Font(None, 36)
        restart_text = font_small.render('Press R to Restart', True, 'white')
        self.display_surface.blit(restart_text, restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50)))

        pygame.display.update()
                
    def restart_game(self):
        self.music.stop()
        self.__init__() # Reinitialize the game      

if __name__ == "__main__":    
    game = Game()
    game.run()
