from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

# --- CẤU HÌNH ĐỘ KHÓ (Dùng Dictionary cho gọn) ---
# Số lượng ô TRỐNG cần tạo ra cho mỗi cấp độ
LEVELS = {
    'easy': 30,     # Dễ: Đục 30 lỗ
    'medium': 45,   # Vừa: Đục 45 lỗ
    'hard': 55,     # Khó: Đục 55 lỗ
    'expert': 60    # Siêu khó: Đục 60 lỗ
}

# --- 1. CORE AI: KIỂM TRA HỢP LỆ ---
def is_valid(board, row, col, num):
    """Kiểm tra xem đặt số 'num' vào vị trí (row, col) có phạm luật không"""
    # 1. Check Hàng & Cột (Gộp chung 1 vòng lặp cho gọn)
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False
            
    # 2. Check Khối 3x3
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

# --- 2. CORE AI: THUẬT TOÁN QUAY LUI (BACKTRACKING) ---
def solve_sudoku(board):
    """Hàm đệ quy tìm lời giải"""
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:  # Tìm thấy ô trống
                for num in range(1, 10): # Thử số 1->9
                    if is_valid(board, row, col, num):
                        board[row][col] = num  # 1. Thử điền
                        
                        if solve_sudoku(board): # 2. Đệ quy giải tiếp
                            return True
                        
                        board[row][col] = 0    # 3. Sai thì Quay lui (Backtrack)
                return False # Thử hết 1-9 mà không được -> Vô nghiệm nhánh này
    return True # Không còn ô trống nào -> Đã giải xong

# --- 3. HỖ TRỢ: SINH ĐỀ & VALIDATE ĐẦU VÀO ---
def validate_input(board):
    """Kiểm tra đề bài người dùng nhập có bị trùng lặp không"""
    for r in range(9):
        for c in range(9):
            if board[r][c] != 0:
                num = board[r][c]
                board[r][c] = 0 # Nhấc quân cờ ra tạm thời
                if not is_valid(board, r, c, num):
                    return False # Nếu đặt lại mà sai -> Đề bài lỗi
                board[r][c] = num # Đặt lại chỗ cũ
    return True

def create_puzzle(level_name):
    """Tạo đề bài mới theo độ khó"""
    # Bước 1: Tạo bảng trắng
    board = [[0]*9 for _ in range(9)]
    
    # Bước 2: Điền ngẫu nhiên đường chéo (để tạo hạt giống khác nhau)
    for i in range(0, 9, 3):
        nums = list(range(1, 10))
        random.shuffle(nums)
        for j in range(3):
            for k in range(3):
                board[i+j][i+k] = nums.pop()
                
    # Bước 3: Giải ra bảng full
    solve_sudoku(board)
    
    # Bước 4: Đục lỗ (Xóa bớt số)
    holes_to_make = LEVELS.get(level_name, 45) # Lấy số lỗ từ Dictionary
    while holes_to_make > 0:
        r, c = random.randint(0, 8), random.randint(0, 8)
        if board[r][c] != 0:
            board[r][c] = 0
            holes_to_make -= 1
    return board

# --- 4. FLASK SERVER (GIAO TIẾP WEB) ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/solve', methods=['POST'])
def api_solve():
    data = request.json
    board = data.get('board')
    
    if not validate_input(board):
        return jsonify({'status': 'fail', 'message': 'Đề bài bị trùng số!'})
        
    if solve_sudoku(board):
        return jsonify({'status': 'success', 'board': board})
    return jsonify({'status': 'fail', 'message': 'Vô nghiệm!'})

@app.route('/generate', methods=['GET'])
def api_generate():
    level = request.args.get('level', 'medium')
    new_board = create_puzzle(level)
    return jsonify({'status': 'success', 'board': new_board})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
