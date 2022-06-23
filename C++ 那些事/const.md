[const](https://hub.nuaa.cf/Light-City/CPlusPlusThings/tree/master/basic_content/const)
## 2.const作用
-   可以定义常量
-   类型检查
**const常量具有类型，编译器可以进行安全检查；#define宏定义没有数据类型，只是简单的字符串替换，不能进行安全检查。**
-   防止修改，起保护作用，增加程序健壮性
 -   可以节省空间，避免不必要的内存分配
    
    -   const定义常量从汇编的角度来看，只是给出了对应的内存地址，而不是像`#define`一样给出的是立即数。
    -   const定义的常量在程序运行过程中只有一份拷贝，而`#define`定义的常量在内存中有若干个拷贝。
## 3.const对象默认为文件局部变量
> 未被const修饰的变量在不同文件的访问
```cpp
// file1.cpp
int ext;
// file2.cpp
#include<iostream>

extern int ext;
int main(){
    std::cout<<(ext+10)<<std::endl;
}
```

> const常量在不同文件的访问

```cpp
//extern_file1.cpp
extern const int ext=12;
//extern_file2.cpp
#include<iostream>
extern const int ext;
int main(){
    std::cout<<ext<<std::endl;
}
```


> 小结：  
> 可以发现未被const修饰的变量不需要extern显式声明！而const常量需要显式声明extern，并且需要做初始化！因为常量在定义后就不能被修改，所以定义时必须初始化。

## 5.指针与const

与指针相关的const有四种：
```cpp
const char * a; //指向const对象的指针或者说指向常量的指针。
char const * a; //同上
char * const a; //指向类型对象的const指针。或者说常指针、const指针。
const char * const a; //指向const对象的const指针。
```


> **小结：**  
> 如果_const_位于`*`的左侧，则const就是用来修饰指针所指向的变量，即指针指向为常量；  
> 如果const位于`*`的右侧，_const_就是修饰指针本身，即指针本身是常量。

（1） **指向常量的指针**
```cpp
const int *ptr;
*ptr = 10; //error
```


ptr是一个指向int类型const对象的指针，const定义的是int类型，也就是ptr所指向的对象类型，而不是ptr本身，所以ptr可以不用赋初始值。但是不能通过ptr去修改所指对象的值。

除此之外，也不能使用void`*`指针保存const对象的地址，必须使用const void`*`类型的指针保存const对象的地址。
```cpp
const int p = 10;
const void * vp = &p;
void *vp = &p; //error
```


另外一个重点是：**允许把非const对象的地址赋给指向const对象的指针**。

将非const对象的地址赋给const对象的指针:
```cpp
const int *ptr;
int val = 3;
ptr = &val; //ok
```


我们不能通过ptr指针来修改val的值，即使它指向的是非const对象!

我们不能使用指向const对象的指针修改基础对象，然而如果该指针指向了非const对象，可用其他方式修改其所指的对象。可以修改const指针所指向的值的，但是不能通过const对象指针来进行而已！如下修改：
```cpp
int *ptr1 = &val;
*ptr1=4;
cout<<*ptr<<endl;
```


> 小结：  
> 1.对于指向常量的指针，不能通过指针来修改对象的值。  
> 2.不能使用void`*`指针保存const对象的地址，必须使用const void`*`类型的指针保存const对象的地址。  
> 3.允许把非const对象的地址赋值给const对象的指针，如果要修改指针所指向的对象值，必须通过其他方式修改，不能直接通过当前指针直接修改。

## 6.函数中使用const
（3）**参数为引用，为了增加效率同时防止修改。**
```cpp
void func(const A &a)
```
	

对于非内部数据类型的参数而言，像void func(A a) 这样声明的函数注定效率比较低。因为函数体内将产生A 类型的临时对象用于复制参数a，而临时对象的构造、复制、析构过程都将消耗时间。

为了提高效率，可以将函数声明改为void func(A &a)，因为“引用传递”仅借用一下参数的别名而已，不需要产生临 时对象。

> 但是函数void func(A &a) 存在一个缺点：  
>   
>** “引用传递”有可能改变参数a，这是我们不期望的。解决这个问题很容易，加const修饰即可，因此函数最终成为 void func(const A &a)。**

以此类推，是否应将void func(int x) 改写为void func(const int &x)，以便提高效率？完全没有必要，因为内部数据类型的参数不存在构造、析构的过程，而复制也非常快，“值传递”和“引用传递”的效率几乎相当。

> 小结：  
> 1.对于**非内部数据类型的输入参数**，**应该将“值传递”的方式改为“const 引用传递”**，目的是提高效率。例如将void func(A a) 改为void func(const A &a)。  
>   
> 2.对于**内部数据类型的输入参数，**不要将“值传递”的方式改为“const 引用传递”。否则既达不到提高效率的目的，又降低了函数的可理解性。例如void func(int x) 不应该改为void func(const int &x)。

以上解决了两个面试问题：

-   如果函数需要传入一个指针，是否需要为该指针加上const，把const加在指针不同的位置有什么区别；
-   如果写的函数需要传入的参数是一个复杂类型的实例，传入值参数或者引用参数有什么区别，什么时候需要为传入的引用参数加上const。