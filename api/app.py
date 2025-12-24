from flask import Flask, render_template, request, jsonify
import random, copy

app = Flask(__name__)

# Cấu hình: Số lượng ô trống sẽ đục lỗ theo từng cấp độ
LEVELS = {
    'easy': 30,     # Dễ
    'medium': 45,   # Trung bình
    'hard': 55,     # Khó
    'expert': 60    # Siêu khó
}

# --- PHẦN 1: LOGIC GAME (CORE) ---

def is_valid(board, r, c, n):
    """Kiểm tra xem đặt số n vào hàng r, cột c có đúng luật không"""
    # 1. Kiểm tra Hàng ngang & Cột dọc
    for i in range(9):
        if board[r][i] == n or board[i][c] == n: return False
    
    # 2. Kiểm tra Khối vuông 3x3
    start_r, start_c = 3 * (r // 3), 3 * (c // 3)
    for i in range(3):
        for j in range(3):
            if board[start_r + i][start_c + j] == n: return False
            
    return True # Hợp lệ

def solve(board):
    """Thuật toán Quay lui (Backtracking) để giải Sudoku"""
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0: # Tìm ô trống
                for n in range(1, 10): # Thử số 1->9
                    if is_valid(board, r, c, n):
                        board[r][c] = n # Thử điền
                        
                        if solve(board): return True # Đệ quy giải tiếp
                        
                        board[r][c] = 0 # Sai thì quay lui (Backtrack)
                return False # Không số nào hợp lệ -> Vô nghiệm
    return True

def validate(board):
    """Kiểm tra đề bài đầu vào có bị trùng số không"""
    for r in range(9):
        for c in range(9):
            if board[r][c] != 0:
                n = board[r][c]
                board[r][c] = 0 # Nhấc ra tạm
                if not is_valid(board, r, c, n): return False # Trùng -> Lỗi
                board[r][c] = n # Đặt lại
    return True

def create_puzzle(level):
    """Quy trình tạo đề bài: Sinh bảng full -> Lưu đáp án -> Đục lỗ"""
    board = [[0]*9 for _ in range(9)]
    
    # Bước 1: Tạo đề bài ngẫu nhiên (để mỗi ván mỗi khác)
    for k in range(0, 9, 3):
        nums = list(range(1, 10))
        random.shuffle(nums)
        for i in range(3):
            for j in range(3):
                board[k+i][k+j] = nums.pop()
    
    # Bước 2: Giải ra bảng hoàn chỉnh
    solve(board)
    
    # Bước 3: Lưu lại bảng đáp án (để tí nữa chấm điểm)
    solution = copy.deepcopy(board) 
    
    # Bước 4: Đục lỗ (Xóa số) tạo thành đề bài
    holes = LEVELS.get(level, 45)
    while holes > 0:
        r, c = random.randint(0, 8), random.randint(0, 8)
        if board[r][c] != 0:
            board[r][c] = 0
            holes -= 1
            
    return board, solution # Trả về cả 2

# --- PHẦN 2: SERVER WEB ---

@app.route('/')
def home(): return render_template('index.html')

@app.route('/solve', methods=['POST'])
def api_solve():
    """API giải giúp (khi người chơi bí)"""
    board = request.json.get('board')
    if not validate(board): return jsonify({'status': 'fail'})
    if solve(board): return jsonify({'status': 'success', 'board': board})
    return jsonify({'status': 'fail'})

@app.route('/generate')
def api_gen():
    """API sinh đề mới (gửi kèm đáp án ngầm)"""
    level = request.args.get('level', 'medium')
    board, solution = create_puzzle(level)
    # Trả về cả board (để chơi) và solution (để chấm)
    return jsonify({'status': 'success', 'board': board, 'solution': solution})

if __name__ == '__main__':
    app.run(debug=True)
