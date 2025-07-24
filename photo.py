import os 
def replace_text_in_file(file_path, old_text, new_text):
     with open(file_path, 'r', encoding='utf-8') as file: 
        file_contents = file.read() 
        new_contents = file_contents.replace(old_text, new_text)
        with open(file_path, 'w', encoding='utf-8') as file: 
            file.write(new_contents) 
def replace_text_in_directory(directory, old_text, new_text): 
    for root, dirs, files in os.walk(directory):
        for file in files: 
            if file.endswith('.md'): 
                file_path = os.path.join(root, file) 
                replace_text_in_file(file_path, old_text, new_text) 
                print(f'Replaced text in {file_path}')

if __name__ == '__main__': 
    directory = './' # 这里填入你想要处理的文件夹路径 
    old_text = 'staticaly.com' 
    new_text = 'jsdelivr.net' 
    replace_text_in_directory(directory, old_text, new_text)