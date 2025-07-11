from networkx.algorithms.matching import max_weight_matching

students = {
    "张三":92,
   "李四":85,
    "王五":78,
    "赵六":95,
    "孙七":88
}
total = 0
max_score = 0
max_name = ""
for name,score in students.items():
    total += score
    if score > max_score:
        max_score = score
        max_name = name
average = total / len(students)
print(f"语文平均成绩:{average:.2f}")
print(f"成绩最高的学生:{max_name},成绩:{max_score}")