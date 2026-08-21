> [!WARNING]
> **本プロジェクトはメンテナンスを終了し、アーカイブされました。**
>
> 今後、本リポジトリの開発およびメンテナンスは行われません。
> 将来的に脆弱性が発見された場合でも、バグ修正やセキュリティパッチの提供は
> 行いません。ご利用は自己責任でお願いします。


# jig-py

Python のソースコードを解析し、設計を支援するためのツールです。

現在はまだ開発中のアルファ版です。対応している機能は以下の通りです。

* [JupyterLab](https://jupyterlab.readthedocs.io/en/stable/) のNotebook上でモジュール依存関係を分析するためのJigモジュール提供
* jig コマンドによるモジュール依存関係の画像出力


解析対象はPython 3のみ対応しています。
互換性のない機能の変更や廃止などがありえます。


## 使い方

pipによるインストール。


```
$ pip install jig-py
```

また、[Graphviz](https://www.graphviz.org/) を別途インストールする必要があります。


JupyterLab Notebook 上での利用方法は[クイックスタート](https://htmlpreview.github.io/?https://github.com/levii/jig-py/blob/master/quick_start.html) を参照してください。
手元のJupyterLabで実行する際には、 quick_start.ipynb ファイルを開いてください。
