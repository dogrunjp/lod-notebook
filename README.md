# 統計LOD NOTEBOOKについて

日本の政府統計をLinked Open Dataとして公開する統計LODは、
難解なエクセルのデータを構造化し機械的な取得を実現した
今後の地域コミュニティへの市民参加に大きな意味を持つサービスですが、
知りたい情報とプロパティを簡単に結びつける手段が今のところ少ないため、
このデータを活かした実効性のあるアウトプットを作るのは現状ではかなり困難です。

統計LODの恩恵を受けるためにはそれなりのデータを扱うための知識が必用そうです。
そのため、このレポジトリではJupyter notebookを使って興味のある政府統計のデータを統計LODから取得しつつ
そのノウハウを蓄積し、できれば共有していきたいと考えています。


- [初めての統計LOD](http://nbviewer.jupyter.org/github/dogrunjp/lod-notebook/blob/master/index.ipynb)
- [統計LODの市町村区のデータを分析](https://github.com/dogrunjp/lod-notebook/blob/master/clustering.ipynb)


※Jupyterにsparql kernelをインストールすると上記の[初めての統計LOD](http://nbviewer.jupyter.org/github/dogrunjp/lod-notebook/blob/master/index.ipynb)が実行できると思います。
githubではsparql kernelがレンダリングされないようなので、プレビューを見たい場合はリンクからご覧ください。


## 法人インフォについて

経済産業省などにより、統計LODと同じように共通語彙基盤を使ってLODとして法人活動情報を公開する
[法人インフォ](http://hojin-info.go.jp/hojin/TopPage)についても、
極基本的なSPARQLのみですがサンプルを公開しています。

- [法人インフォメーションAPI利用ノート](https://github.com/dogrunjp/lod-notebook/blob/master/hojin-info.ipynb)

- [Python-SPARQLWrapperによる法人インフォの利用](https://github.com/dogrunjp/lod-notebook/blob/master/hojin-info-py.ipynb)

- [D3.jsによる法人インフォの利用](https://github.com/dogrunjp/lod-notebook/blob/master/hojin-info-d3.ipynb)
