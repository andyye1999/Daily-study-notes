```   
git init //把这个目录变成Git可以管理的仓库
git add README.md //文件添加到仓库
git add . //不但可以跟单一文件，还可以跟通配符，更可以跟目录。一个点就把当前目录下所有未追踪的文件全部add了 
git commit -m "first commit" //把文件提交到仓库
git remote add origin git@github.com:wangjiax9/practice.git //关联远程仓库
git pull --rebase origin master
git pull origin master
git push -u origin master //把本地库的所有内容推送到远程库上  
git stash
```

```
git rm -r -n --cached 文件/文件夹名称 
 
加上 -n 这个参数，执行命令时，是不会删除任何文件，而是展示此命令要删除的文件列表预览。
确定无误后删除文件
git rm -r --cached 文件/文件夹名称
git commit -m "提交说明"
git push origin master
```