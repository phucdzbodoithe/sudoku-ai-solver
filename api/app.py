from flask import Flask, render_template, request, jsonify
import random, copy

app = Flask(__name__)

# Cấu hình số ô bị đục lỗ
LEVELS = {'easy': 30, 'medium': 45, 'hard': 55, 'expert': 60}

# --- THUẬT TOÁN (Chuẩn theo ý tưởng nhóm) ---

def is_valid(board, r, c, n):
    """Kiểm tra hợp lệ để dùng cho quay lui"""
    for i in range(9):
        if board[r][i] == n or board[i][c] == n: return False
    sr, sc = 3 * (r // 3), 3 * (c // 3)
    for i in range(3):
        for j in range(3):
            if board[sr+i][sc+j] == n: return False
    return True

def solve(board):
    """Thuật toán Quay lui (Backtracking) để điền đầy bảng"""
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

def create_puzzle(level):
    # B1: Tạo bảng rỗng
    board = [[0]*9 for _ in range(9)]
    
    # B2: "Điền 1 số random từ 1-9 vào ô" (Gieo hạt giống)
    # Mình gieo 3 khối chéo để đảm bảo tính ngẫu nhiên cao nhất
    for k in range(0, 9, 3):
        nums = list(range(1, 10))
        random.shuffle(nums)
        for i in range(3):
            for j in range(3):
                board[k+i][k+j] = nums.pop()
    
    # B3: "Chạy 1 phát là ra matrix kq thoả mãn"
    solve(board)
    
    # B4: "Lưu matrix này vào 1 biến" (Quan trọng!)
    solution = copy.deepcopy(board) 
    
    # B5: "Đi đục lỗ cái kq có sẵn"
    holes = LEVELS.get(level, 45)
    while holes > 0:
        r, c = random.randint(0, 8), random.randint(0, 8)
        if board[r][c] != 0:
            board[r][c] = 0
            holes -= 1
            
    # Trả về cả Bảng chơi (board) và Đáp án gốc (solution)
    return board, solution

# --- SERVER ---
@app.route('/')
def home(): return render_template('index.html')

@app.route('/solve', methods=['POST'])
def api_solve():
    # Phần AI giải hộ: Nhận bảng về và giải lại từ đầu
    board = request.json.get('board')
    # Gọi hàm solve để điền nốt các ô trống
    if solve(board): 
        return jsonify({'status': 'success', 'board': board})
    return jsonify({'status': 'fail'})

@app.route('/generate')
def api_gen():
    level = request.args.get('level', 'medium')
    board, solution = create_puzzle(level)
    return jsonify({'status': 'success', 'board': board, 'solution': solution})

if __name__ == '__main__':
    app.run(debug=True)
