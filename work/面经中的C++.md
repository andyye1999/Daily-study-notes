
# C++中的虚函数是用来干什么的


# 多线程和多进程的区别


# 32位和64位操作系统编程的区别

32位操作系统的内存限制为4GB，它只能对2^32个字节的内存进行地址分配。这限制了32位操作系统在处理需要大量内存的任务时的性能。

64位操作系统则没有这个限制，它可以对更大的内存进行地址分配，因此能够更有效地处理大型的数据和任务。

# C++中malloc/free 和new/delete的区别


# 指针和引用的区别



# shell命令

[shell脚本]([一篇教会你写90%的shell脚本 - 知乎 (zhihu.com)](https://zhuanlan.zhihu.com/p/264346586))


# 二叉树递归

**如果需要搜索整棵二叉树，那么递归函数就不要返回值，如果要搜索其中一条符合条件的路径，递归函数就需要返回值，因为遇到符合条件的路径了就要及时返回。**

如果递归函数有返回值，如何区分要搜索一条边，还是搜索整个树呢？

搜索一条边的写法：
```
if (递归函数(root->left)) return ;

if (递归函数(root->right)) return ;
```
搜索整个树写法：
```
left = 递归函数(root->left);  // 左
right = 递归函数(root->right); // 右
left与right的逻辑处理;         // 中 
```
看出区别了没？

**在递归函数有返回值的情况下：如果要搜索一条边，递归函数返回值不为空的时候，立刻返回，如果搜索整个树，直接用一个变量left、right接住返回值，这个left、right后序还有逻辑处理的需要，也就是后序遍历中处理中间节点的逻辑（也是回溯）**。

那么为什么要遍历整棵树呢？直观上来看，找到最近公共祖先，直接一路返回就可以了。

**那么我给大家归纳如下三点**：

求最小公共祖先，需要从底向上遍历，那么二叉树，只能通过后序遍历（即：回溯）实现从底向上的遍历方式。

在回溯的过程中，必然要遍历整棵二叉树，即使已经找到结果了，依然要把其他节点遍历完，因为要使用递归函数的返回值（也就是代码中的left和right）做逻辑判断。

要理解如果返回值left为空，right不为空为什么要返回right，为什么可以用返回right传给上一层结果。

# 指针常量 常量指针

![image](https://cdn.staticaly.com/gh/andyye1999/picx-images-hosting@master/20230511/image.2xrwxuw0g500.webp)

# 大顶堆 优先队列

[剑指 Offer 41. 数据流中的中位数](https://leetcode.cn/problems/shu-ju-liu-zhong-de-zhong-wei-shu-lcof)

[347. 前 K 个高频元素](https://leetcode.cn/problems/top-k-frequent-elements)

[239. 滑动窗口最大值](https://leetcode.cn/problems/sliding-window-maximum) 单调队列或者优先队列  

[23. 合并K个排序链表](https://leetcode.cn/problems/merge-k-sorted-lists)



```cpp
less<int> // 大顶堆
greater<int> // 小顶堆 
priority_queue<int,vector<int>,less<int>> maxHeap;
```

要么
```cpp
struct cmp
{
	bool operator()(int a,int b)
	{
		return a < b;  // 大顶堆
	}
};
```

# 万能头文件 

```cpp
#include <bits/stdc++.h>
```