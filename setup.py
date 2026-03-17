from setuptools import setup, find_packages

setup(
    name="rootengine",                 # 包名（安装时名字）
    version="0.1.0",                          # 版本号
    packages=find_packages(),                  # 自动发现所有包

    install_requires=[                         # 依赖的第三方库
        "openai>=1.0.0",                       # OpenAI 库
    ],
    author="zimvir",                          # 作者名字
    author_email="zimvir@qq.com",                    # 邮箱
    description="一个 单AI Agent 框架",   # 简短描述
    python_requires=">=3.8",                   # 最低 Python 版本要求

    url="https://github.com/zimvir/RootEngine",   # 项目主页
    classifiers=[                               # 分类信息
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)