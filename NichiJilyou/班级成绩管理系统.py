# # 定义学生类
# class Student:
#     def __init__(self, student_id, name, gender, score1, score2, score3):
#         self.student_id = student_id
#         self.name = name
#         self.gender = gender
#         self.score1 = score1
#         self.score2 = score2
#         self.score3 = score3
#
#         # 可以添加其他方法，如打印学生信息、验证成绩合法性等
#
#     def __str__(self):
#         return f"ID: {self.student_id}, Name: {self.name}, Gender: {self.gender}, Scores: {self.score1}, {self.score2}, {self.score3}"
# # 实现功能模块
# def input_student_info():
#     student_id = input("Enter student ID: ")
#     # 这里应该添加逻辑来检查学号是否已存在，但为简化省略
#     name = input("Enter student name: ")
#     gender = input("Enter student gender (M/F): ").upper()
#     score1 = int(input("Enter score 1: "))
#     score2 = int(input("Enter score 2: "))
#     score3 = int(input("Enter score 3: "))
#
#     return Student(student_id, name, gender, score1, score2, score3)
#
# # 显示模块
# def display_students(students):
#     if not students:
#         print("No students found.")
#         return
#     for student in students:
#         print(student)
#
#         # 注：这里假设有一个students列表作为参数传入
# # 查询模块
# def find_student_by_name(students, name):
#     for student in students:
#         if student.name == name:
#             return student
#     return None
#
#     # 注：这里假设有一个students列表和一个要查询的姓名作为参数传入
#
# 优化总和
class Student:
    def __init__(self, student_id, name, gender, score1, score2, score3):
        self.student_id = student_id
        self.name = name
        self.gender = gender
        self.score1 = score1
        self.score2 = score2
        self.score3 = score3

    def __str__(self):
        return f"ID: {self.student_id}, Name: {self.name}, Gender: {self.gender}, Scores: {self.score1}, {self.score2}, {self.score3}"


students = []


def input_student_info():
    while True:
        student_id = input("Enter student ID (or 'q' to quit): ").strip()
        if student_id.lower() == 'q':
            break
        if student_id in [student.student_id for student in students]:
            print("Error: Student ID already exists.")
            continue

        name = input("Enter student name: ")
        gender = input("Enter student gender (M/F): ").upper()
        if gender not in ['M', 'F']:
            print("Error: Invalid gender. Please enter 'M' or 'F'.")
            continue

        try:
            score1 = int(input("Enter score 1: "))
            score2 = int(input("Enter score 2: "))
            score3 = int(input("Enter score 3: "))
        except ValueError:
            print("Error: Scores must be integers.")
            continue

        students.append(Student(student_id, name, gender, score1, score2, score3))
        print("Student added successfully!")


def display_students():
    if not students:
        print("No students found.")
        return
    for student in students:
        print(student)


def find_student_by_name(name):
    for student in students:
        if student.name == name:
            return student
    return None


def calculate_statistics():
    # 简化的统计实现
    gender_scores = {'M': [0, 0, 0], 'F': [0, 0, 0]}
    for student in students:
        gender_scores[student.gender][0] += student.score1
        gender_scores[student.gender][1] += student.score2
        gender_scores[student.gender][2] += student.score3

    total_students = {'M': 0, 'F': 0}
    for gender, scores in gender_scores.items():
        count = sum(1 for score in scores if score > 0)  # 计算有成绩的学生数（简化处理）
        if count > 0:
            avg_scores = [score / count for score in scores]
            print(f"Average Scores for {gender}: {avg_scores}")
            total_students[gender] = count

    print(f"Total Students: M={total_students['M']}, F={total_students['F']}")


def main_menu():
    while True:
        print("\n1. Input student info")
        print("2. Display all students")
        print("3. Find student by name")
        print("4. Calculate statistics")
        print("5. Exit")
        choice = input("Enter your choice (1-5): ")

        if choice == '1':
            input_student_info()
        elif choice == '2':
            display_students()
        elif choice == '3':
            name = input("Enter student name to find: ")
            found_student = find_student_by_name(name)
            if found_student:
                print(found_student)
            else:
                print("Student not found.")
        elif choice == '4':
            calculate_statistics()
        elif choice == '5':
            print("Exiting the system...")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main_menu()
