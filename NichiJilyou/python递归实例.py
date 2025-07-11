# 计算阶乘
def factroial(n):
    if n == 0:
        return 1  # 终止条件，n的阶乘为1
    else:
        return n * factroial(n - 1)  # 递归调用，计算n的阶乘


# 斐波那契数列
def fibonacci(n):
    if n <= 1:
        return n  # 终止条件，0的阶乘为1
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)  # 递归调用，计算第n个斐波那契数


# 二叉树遍历
class BTree(object):
    def __init__(self, data=None, left=None, right=None):
        self.data = data  # 数据域
        self.left = left  # 左子树
        self.right = right  # 右子树

    # 前序遍历：中，左，右
    def preorder(self):
        if self.data:
            print(self.data, end='')
        if self.left:
            self.left.preorder()
        if self.right:
            self.right.preorder()

    # 中序遍历：左，中，右
    def inorder(self):
        if self.left:
            self.left.inorder()
        if self.data:
            print(self.data, end='')
        if self.right:
            self.right.inorder()

    # 后序遍历：左,右,中
    def postorder(self):
        if self.left:
            self.left.postorder()
        if self.right:
            self.right.postorder()
        if self.data:
            print(self.data, end='')

# 层序遍历：

