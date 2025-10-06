import pygame
import sys
import math
import re

pygame.init()

WIDTH, HEIGHT = 700, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame 科学计算器")

WHITE = (255, 255, 255)
GRAY = (230, 230, 230)
DARKGRAY = (150, 150, 150)
BLACK = (0, 0, 0)
BLUE = (80, 160, 220)
ORANGE = (255, 165, 0)
RED = (220, 80, 80)
GREEN = (90, 180, 120)
PURPLE = (180, 90, 220)

font = pygame.font.SysFont(None, 54)
small_font = pygame.font.SysFont(None, 32)

# 科学计算器按钮布局（删除了^和in/ln）
buttons = [
    ['MC', 'MR', 'M+', 'M-', 'C', '(', ')', '√'],
    ['sin', 'cos', 'tan', 'log', 'π', 'e', '!', '%'],
    ['7', '8', '9', '/', '//', '*', '', '', ''],
    ['4', '5', '6', '-', '', '', '', '', ''],
    ['1', '2', '3', '+', '', '', '', '', ''],
    ['0', '.', '=', '', '', '', '', '', '']
]

btn_w, btn_h = 65, 65
margin_left = 18
margin_top = 210
btn_gap = 11

button_rects = []
for row_idx, row in enumerate(buttons):
    for col_idx, label in enumerate(row):
        if label.strip() == '':
            continue
        rect = pygame.Rect(
            margin_left + col_idx * (btn_w + btn_gap),
            margin_top + row_idx * (btn_h + btn_gap),
            btn_w, btn_h
        )
        button_rects.append((rect, label))

current = ""
result = ""
memory = 0.0
memory_set = False
error_state = False

def format_result(res):
    try:
        if isinstance(res, float) and res.is_integer():
            return str(int(res))
        return str(res)
    except:
        return str(res)

def safe_eval(expr):
    try:
        # 处理 (表达式)! 阶乘写法
        expr = re.sub(r'(\([^()]+\))!', r'math.factorial\1', expr)
        # 处理数字阶乘
        expr = re.sub(r'(\d+)!', r'math.factorial(\1)', expr)
        # 百分号：数字或括号后跟%转为/100
        expr = re.sub(r'(\d+(\.\d+)?|\([^()]+\))%', r'(\1)/100', expr)
        # 科学符号与函数
        expr = expr.replace('π', str(math.pi)).replace('e', str(math.e))
        expr = expr.replace('√', 'math.sqrt')
        expr = expr.replace('log', 'math.log10')
        expr = expr.replace('sin', 'math.sin')
        expr = expr.replace('cos', 'math.cos')
        expr = expr.replace('tan', 'math.tan')
        # 支持角度转弧度输入
        expr = re.sub(r'math\.(sin|cos|tan)\(([^)]+)\)',
                      lambda m: f"math.{m.group(1)}(math.radians({m.group(2)}))", expr)
        # 检查除数为0，支持多位数字
        if re.search(r'(/|//|%)\s*0+(\D|$)', expr):
            return "错误"
        res = eval(expr, {"math": math, "__builtins__": {}})
        return format_result(res)
    except:
        return "错误"

def draw(mem_value):
    screen.fill(WHITE)
    pygame.draw.rect(screen, GRAY, [20, 40, 660, 140], border_radius=10)
    if current:
        show_text = current
    elif result:
        show_text = result
    else:
        show_text = "0"
    mem_text = f"M: {format_result(mem_value)}" if memory_set else ""
    m_text = small_font.render(mem_text, True, PURPLE)
    screen.blit(m_text, (30, 55))
    if len(show_text) > 20:
        show_text = show_text[-20:]
    text = font.render(show_text, True, BLACK)
    screen.blit(text, (30, 130 - text.get_height() // 2))
    for rect, label in button_rects:
        if label in ('MC', 'MR', 'M+', 'M-'):
            color = PURPLE
        elif label == 'C':
            color = RED
        elif label == '=':
            color = ORANGE
        elif label in ('+', '-', '*', '/', '%', '//', '√', '!'):
            color = BLUE
        elif label in ('sin', 'cos', 'tan', 'log', 'π', 'e'):
            color = GREEN
        else:
            color = DARKGRAY
        pygame.draw.rect(screen, color, rect, border_radius=8)
        pygame.draw.rect(screen, BLACK, rect, 2, border_radius=8)
        label_text = small_font.render(label, True, WHITE)
        x = rect.x + (btn_w - label_text.get_width()) // 2
        y = rect.y + (btn_h - label_text.get_height()) // 2
        screen.blit(label_text, (x, y))
    pygame.display.flip()

while True:
    draw(memory)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for rect, label in button_rects:
                if rect.collidepoint(pos):
                    if label == 'C':
                        current = ""
                        result = ""
                        error_state = False
                    elif label == '=':
                        eval_result = safe_eval(current)
                        if eval_result == "错误":
                            current = "错误"
                            result = ""
                            error_state = True
                        else:
                            result = eval_result
                            current = ""
                            error_state = False
                    elif label == 'MC':
                        memory = 0.0
                        memory_set = False
                    elif label == 'MR':
                        if memory_set:
                            mem_str = format_result(memory)
                            if error_state or current == "错误":
                                current = mem_str
                            else:
                                current += mem_str
                        result = ""
                    elif label == 'M+':
                        try:
                            val = float(result) if result else (
                                float(safe_eval(current)) if current else 0.0)
                            memory += val
                            memory_set = True
                        except:
                            pass
                        result = ""
                        current = ""
                        error_state = False
                    elif label == 'M-':
                        try:
                            val = float(result) if result else (
                                float(safe_eval(current)) if current else 0.0)
                            memory -= val
                            memory_set = True
                        except:
                            pass
                        result = ""
                        current = ""
                        error_state = False
                    else:
                        if result or error_state or current == "错误":
                            result = ""
                            current = ""
                            error_state = False
                        if label in ['π', 'e']:
                            current += label
                        elif label == '√':
                            current += '√('
                        elif label in ['sin', 'cos', 'tan', 'log']:
                            current += label + '('
                        elif label == '!':
                            current += '!'
                        else:
                            current += label