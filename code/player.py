from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        self.load_images()
        self.state, self.frame_index = 'down', 0
        self.image = pygame.image.load(join('images', 'player', 'down', '0.png')).convert_alpha()
        self.rect = self.image.get_frect(center=pos)
        self.hitbox_rect = self.rect.inflate(-60,-90)

        # movement
        self.direction = pygame.Vector2(0,0)
        self.speed = 500
        self.collision_sprites = collision_sprites

        # health
        self.health = 3
        self.alive = True

        # invincibility
        self.invincible = False
        self.hit_time = 0
        self.invincibility_duration = 1000  # milliseconds
    
    def load_images(self):
        self.frames ={'left': [], 'right': [], 'up': [], 'down': []}

        for state in self.frames.keys():
            for folder_path, sub_folders, file_names in walk(join('images', 'player', state)):
                if file_names:
                    for file_name in sorted(file_names, key=lambda name: int(name.split('.')[0])):
                        full_path = join(folder_path, file_name)                        
                        surf = pygame.image.load(full_path).convert_alpha()
                        self.frames[state].append(surf)
              
    def take_damage(self):
        current_time = pygame.time.get_ticks()
        if not self.invincible:
            self.health -= 1
            self.invincible = True
            self.hit_time = current_time
            if self.health <= 0:
                self.alive = False       

    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = (
            int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT]) +
            int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        )
        self.direction.y = (
            int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP]) +
            int(keys[pygame.K_s]) - int(keys[pygame.K_w])
        )
        self.direction = self.direction.normalize() if self.direction else self.direction
    
    def move(self, dt):
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')
        self.rect.center = self.hitbox_rect.center

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0:
                        self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0:
                        self.hitbox_rect.left = sprite.rect.right
                else:
                    if self.direction.y > 0:
                        self.hitbox_rect.bottom = sprite.rect.top
                    if self.direction.y < 0:
                        self.hitbox_rect.top = sprite.rect.bottom

    def animate(self, dt):
        # get state
        if self.direction.x < 0:
            self.state = 'left'
        elif self.direction.x > 0:
            self.state = 'right'
        elif self.direction.y < 0:
            self.state = 'up'
        elif self.direction.y > 0:
            self.state = 'down'

        # animate only if moving
        if self.direction.magnitude() != 0:
            self.frame_index += 5 * dt

        # update image
        self.image = self.frames[self.state][int(self.frame_index) % len(self.frames[self.state])]

    def update(self, dt):
        self.input()
        self.move(dt)
        self.animate(dt)
        if self.invincible:
            current_time = pygame.time.get_ticks()
            if current_time - self.hit_time >= self.invincibility_duration:
                self.invincible = False
                self.image.set_alpha(255)  # Reset alpha to fully visible
            else:
                # Flash effect
                if (current_time // 100) % 2 == 0:
                    self.image.set_alpha(100) # transparent               
                else:
                    self.image.set_alpha(255) # fully visible
        else:
            self.image.set_alpha(255) # Reset alpha to fully visible
