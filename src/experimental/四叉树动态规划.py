import pygame
import sys
import random
import math
import time
from typing import List, Tuple, Optional

# 初始化pygame
pygame.init()

# 屏幕设置
WIDTH, HEIGHT = 1800, 1200
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Demonstration of the collision algorithm for dynamic programming of quadtree trees")

# 颜色定义
BACKGROUND = (10, 10, 40)
QUADTREE_COLOR = (70, 130, 180)
PARTICLE_COLORS = [
    (220, 20, 60),    # 红色
    (255, 140, 0),    # 橙色
    (255, 215, 0),    # 金色
    (50, 205, 50),    # 绿色
    (30, 144, 255),   # 蓝色
    (138, 43, 226),   # 紫色
]
COLLISION_COLOR = (255, 255, 0)  # 黄色表示碰撞
TEXT_COLOR = (220, 220, 255)
GRID_COLOR = (40, 40, 80)

# 粒子类
class Particle:
    def __init__(self, x: float, y: float, radius: float):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = random.choice(PARTICLE_COLORS)
        self.vx = random.uniform(-1.5, 1.5)
        self.vy = random.uniform(-1.5, 1.5)
        self.colliding = False
    
    def move(self):
        self.x += self.vx
        self.y += self.vy
        
        # 边界反弹
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx = -self.vx * 0.9
        elif self.x + self.radius > WIDTH:
            self.x = WIDTH - self.radius
            self.vx = -self.vx * 0.9
        
        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy = -self.vy * 0.9
        elif self.y + self.radius > HEIGHT:
            self.y = HEIGHT - self.radius
            self.vy = -self.vy * 0.9
    
    def draw(self, surface):
        # 绘制粒子
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        
        # 如果碰撞，绘制高亮边框
        if self.colliding:
            pygame.draw.circle(surface, COLLISION_COLOR, (int(self.x), int(self.y)), self.radius + 2, 2)

# 四叉树节点类
class QuadtreeNode:
    def __init__(self, x: float, y: float, width: float, height: float, capacity: int = 4, level: int = 0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.capacity = capacity
        self.level = level
        self.particles: List[Particle] = []
        self.divided = False
        
        # 子节点
        self.nw: Optional[QuadtreeNode] = None
        self.ne: Optional[QuadtreeNode] = None
        self.sw: Optional[QuadtreeNode] = None
        self.se: Optional[QuadtreeNode] = None
    
    def contains(self, particle: Particle) -> bool:
        return (self.x <= particle.x <= self.x + self.width and 
                self.y <= particle.y <= self.y + self.height)
    
    def intersects(self, x: float, y: float, radius: float) -> bool:
        # 检查圆形是否与矩形区域相交
        closest_x = max(self.x, min(x, self.x + self.width))
        closest_y = max(self.y, min(y, self.y + self.height))
        distance_x = x - closest_x
        distance_y = y - closest_y
        return (distance_x ** 2 + distance_y ** 2) < (radius ** 2)
    
    def subdivide(self):
        half_w = self.width / 2
        half_h = self.height / 2
        
        self.nw = QuadtreeNode(self.x, self.y, half_w, half_h, self.capacity, self.level + 1)
        self.ne = QuadtreeNode(self.x + half_w, self.y, half_w, half_h, self.capacity, self.level + 1)
        self.sw = QuadtreeNode(self.x, self.y + half_h, half_w, half_h, self.capacity, self.level + 1)
        self.se = QuadtreeNode(self.x + half_w, self.y + half_h, half_w, half_h, self.capacity, self.level + 1)
        
        self.divided = True
        
        # 将粒子重新插入到子节点中
        for particle in self.particles:
            if self.nw.contains(particle):
                self.nw.insert(particle)
            elif self.ne.contains(particle):
                self.ne.insert(particle)
            elif self.sw.contains(particle):
                self.sw.insert(particle)
            elif self.se.contains(particle):
                self.se.insert(particle)
        
        self.particles = []
    
    def insert(self, particle: Particle) -> bool:
        if not self.contains(particle):
            return False
        
        if len(self.particles) < self.capacity and not self.divided:
            self.particles.append(particle)
            return True
        
        if not self.divided and self.level < 6:  # 限制最大深度
            self.subdivide()
        
        if self.divided:
            return (self.nw.insert(particle) or
                    self.ne.insert(particle) or
                    self.sw.insert(particle) or
                    self.se.insert(particle))
        
        # 如果容量已满且无法再分割，直接添加到当前节点
        self.particles.append(particle)
        return True
    
    def query(self, x: float, y: float, radius: float, found: List[Particle]) -> None:
        if not self.intersects(x, y, radius):
            return
        
        for particle in self.particles:
            distance = math.sqrt((x - particle.x) ** 2 + (y - particle.y) ** 2)
            if distance < radius + particle.radius:
                found.append(particle)
        
        if self.divided:
            self.nw.query(x, y, radius, found)
            self.ne.query(x, y, radius, found)
            self.sw.query(x, y, radius, found)
            self.se.query(x, y, radius, found)
    
    def draw(self, surface):
        # 绘制四叉树边界
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, QUADTREE_COLOR, rect, 1)
        
        # 绘制子节点
        if self.divided:
            self.nw.draw(surface)
            self.ne.draw(surface)
            self.sw.draw(surface)
            self.se.draw(surface)

# 创建粒子
def create_particles(num_particles: int) -> List[Particle]:
    particles = []
    for _ in range(num_particles):
        radius = random.randint(8, 20)
        x = random.randint(radius, WIDTH - radius)
        y = random.randint(radius, HEIGHT - radius)
        
        # 确保粒子不会重叠
        valid_position = True
        for p in particles:
            distance = math.sqrt((x - p.x) ** 2 + (y - p.y) ** 2)
            if distance < radius + p.radius:
                valid_position = False
                break
        
        if valid_position:
            particles.append(Particle(x, y, radius))
    
    return particles

# 暴力碰撞检测（用于对比）
def brute_force_collision(particles: List[Particle]) -> int:
    collisions = 0
    for i in range(len(particles)):
        particles[i].colliding = False
    
    for i in range(len(particles)):
        for j in range(i + 1, len(particles)):
            p1 = particles[i]
            p2 = particles[j]
            distance = math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)
            if distance < p1.radius + p2.radius:
                p1.colliding = True
                p2.colliding = True
                collisions += 1
    
    return collisions

# 使用四叉树的碰撞检测
def quadtree_collision(particles: List[Particle], quadtree: QuadtreeNode) -> int:
    collisions = 0
    for particle in particles:
        particle.colliding = False
    
    for particle in particles:
        candidates = []
        quadtree.query(particle.x, particle.y, particle.radius, candidates)
        
        for candidate in candidates:
            if candidate is particle:
                continue
            distance = math.sqrt((particle.x - candidate.x) ** 2 + (particle.y - candidate.y) ** 2)
            if distance < particle.radius + candidate.radius:
                particle.colliding = True
                candidate.colliding = True
                collisions += 1
    
    return collisions // 2  # 因为每个碰撞被计数两次

# 创建四叉树
quadtree = QuadtreeNode(0, 0, WIDTH, HEIGHT, 4)

# 创建粒子
particles = create_particles(1800)

# 字体设置
font = pygame.font.SysFont(None, 24)
title_font = pygame.font.SysFont(None, 36)

# 主循环
clock = pygame.time.Clock()
paused = False
show_quadtree = True
show_grid = False
brute_force_mode = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_q:
                show_quadtree = not show_quadtree
            elif event.key == pygame.K_g:
                show_grid = not show_grid
            elif event.key == pygame.K_b:
                brute_force_mode = not brute_force_mode
            elif event.key == pygame.K_r:
                particles = create_particles(80)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # 添加新粒子
            x, y = pygame.mouse.get_pos()
            radius = random.randint(8, 20)
            particles.append(Particle(x, y, radius))
    
    if not paused:
        # 移动粒子
        for particle in particles:
            particle.move()
        
        # 重建四叉树
        quadtree = QuadtreeNode(0, 0, WIDTH, HEIGHT, 4)
        for particle in particles:
            quadtree.insert(particle)
        
        # 检测碰撞
        start_time = time.perf_counter()
        if brute_force_mode:
            collisions = brute_force_collision(particles)
            method = "Brute force detection"
        else:
            collisions = quadtree_collision(particles, quadtree)
            method = "Quadtree detection"
        collision_time = (time.perf_counter() - start_time) * 1000  # 毫秒
    
    # 绘制
    screen.fill(BACKGROUND)
    
    # 绘制网格（如果启用）
    if show_grid:
        for x in range(0, WIDTH, 20):
            pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, 20):
            pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y), 1)
    
    # 绘制四叉树（如果启用）
    if show_quadtree:
        quadtree.draw(screen)
    
    # 绘制粒子
    for particle in particles:
        particle.draw(screen)
    
    # 绘制UI
    pygame.draw.rect(screen, (20, 20, 50, 180), (0, 0, WIDTH, 90))
    
    # 标题
    title = title_font.render("Demonstration of the quadtree dynamic programming collision algorithm", True, (255, 215, 0))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 10))
    
    # 统计信息
    stats_text = [
        f"Number of particles: {len(particles)}",
        f"Number of collision logarithms: {collisions}",
        f"Detection method: {method}",
        f"Detection time: {collision_time:.3f} ms"
    ]
    
    for i, text in enumerate(stats_text):
        text_surface = font.render(text, True, TEXT_COLOR)
        screen.blit(text_surface, (20, 40 + i * 20))
    
    # 控制说明
    controls = [
    "Space: Pause/Resume Q: Show/Hide Quadtree",
    "G: Show/Hide Mesh B: Toggle Detection method",
    "R: Reset Particles Mouse Click: Add Particles"
    ]
    
    for i, text in enumerate(controls):
        text_surface = font.render(text, True, (180, 180, 255))
        screen.blit(text_surface, (WIDTH - 380, 40 + i * 20))
    
    pygame.display.flip()
    clock.tick(60)