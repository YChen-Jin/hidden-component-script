import os

# 定义查找网络请求相关的关键词
network_keywords = [
    'Ljava/net/HttpURLConnection;',
    'Lcom/squareup/okhttp3/OkHttpClient;',
    'Lretrofit2/Retrofit;',
    'Landroid/net/Uri;',
    'Lorg/apache/http/client/methods/HttpGet;',
    'Lorg/apache/http/client/methods/HttpPost;',
    'Lorg/apache/http/impl/client/DefaultHttpClient;'
]


# 遍历目录并查找网络请求相关代码
def search_network_requests(apk_dir):
    # 遍历 APK 文件夹中的所有 Smali 文件
    for root, dirs, files in os.walk(apk_dir):
        for file in files:
            # 只处理 Smali 文件
            if file.endswith('.smali'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        smali_code = f.read()
                        # 检查是否有网络请求相关的关键词
                        for keyword in network_keywords:
                            if keyword in smali_code:
                                print(f"Found '{keyword}' in file: {file_path}")
                except FileNotFoundError:
                    # 如果找不到文件，打印错误信息并跳过
                    print(f"File not found: {file_path}")
                    continue
                except Exception as e:
                    # 捕获其他可能的异常
                    print(f"Error processing file {file_path}: {e}")
                    continue
    # 添加分割线，便于观察
    print("\n" + "=" * 50 + "\n")


# 主函数
def main():
    base_dir = r"D:\code\must\15apk\apk"  # 基础目录
    # 获取所有 APK 包的目录
    apk_dirs = [os.path.join(base_dir, folder) for folder in os.listdir(base_dir) if
                os.path.isdir(os.path.join(base_dir, folder))]

    for apk_dir in apk_dirs:
        signed_dir = os.path.join(apk_dir, f"{os.path.basename(apk_dir)}-signed")
        if os.path.isdir(signed_dir):
            print(f"Searching in: {signed_dir}")
            search_network_requests(signed_dir)


if __name__ == "__main__":
    main()
