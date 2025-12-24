from flask import Flask, render_template, request, jsonify
import random, copy

app = Flask(__name__)

# Cấu hình độ khó
LEVELS = {'easy': 30, 'medium': 45, 'hard': 55, 'expert': 60}

# --- LOGIC XỬ LÝ ---
def is_valid(board, r, c, n):
    for i in range(9):
        if board[r][i] == n or board[i][c] == n: return False
    sr, sc = 3 * (r // 3), 3 * (c // 3)
    for i in range(3):
        for j in range(3):
            if board[sr+i][sc+j] == n: return False
    return True

def solve(board):
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                for n in range(1, 10):
                    if is_valid(board, r, c, n):
                        board[r][c] = n
                        if solve(board): return True
                        board[r][c] = 0
                return False
    return True

def validate(board):
    for r in range(9):
        for c in range(9):
            if board[r][c] != 0:
                n = board[r][c]
                board[r][c] = 0
                if not is_valid(board, r, c, n): return False
                board[r][c] = n
    return True

def create_puzzle(level):
    board = [[0]*9 for _ in range(9)]
    # Tạo đề bài ngẫu nhiên
    for k in range(0, 9, 3):
        nums = list(range(1, 10))
        random.shuffle(nums)
        for i in range(3):
            for j in range(3):
                board[k+i][k+j] = nums.pop()
    
    solve(board)
    # LƯU ĐÁP ÁN LẠI TRƯỚC KHI ĐỤC LỖ
    solution = copy.deepcopy(board)
    
    # Đục lỗ
    holes = LEVELS.get(level, 45)
    while holes > 0:
        r, c = random.randint(0, 8), random.randint(0, 8)
        if board[r][c] != 0:
            board[r][c] = 0
            holes -= 1
    return board, solution

# --- SERVER ---
@app.route('/')
def home(): return render_template('index.html')

@app.route('/solve', methods=['POST'])
def api_solve():
    board = request.json.get('board')
    if not validate(board): return jsonify({'status': 'fail'})
    if solve(board): return jsonify({'status': 'success', 'board': board})
    return jsonify({'status': 'fail'})

@app.route('/generate')
def api_gen():
    level = request.args.get('level', 'medium')
    # Lấy cả đề bài và đáp án
    board, solution = create_puzzle(level)
    return jsonify({'status': 'success', 'board': board, 'solution': solution})

if __name__ == '__main__':
    app.run(debug=True)
