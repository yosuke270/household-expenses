# Azureを使った環境構築

## アーキテクチャ設計
1. モノリシックアーキテクチャ　vs　マイクロサービスアーキテクチャ
   - モノリシックアーキテクチャ
   　アプリケーションを構成する処理が単一のサービスとして実行される。
   　処理が強く結びついているので、どこが出エラーが生じるとアーキテクチャ全体が停止してしまう。
   　また機能を増やそうとすると、テストする項目も増える。

   - マイクロサービスアーキテクチャ
     アプリケーションが独立した複数のコンポーネントから構成される。
     各コンポーネントは1つのサービスとして個別にアプリケーションを実行する。
     __サービス間は厳格に定義されたAPIを通じてやり取りをする。__
     各サービスは独立している為、メンテナンス性や保守性が向上する。

   　参考： [マイクロサービス](https://aws.amazon.com/jp/microservices/)

2. マイクロサービス向けのサービス
   - コンテナ
     Amazon Elastic Container Service
     Azure Container Apps
     [Azure と AWS のコンピューティング サービス](https://learn.microsoft.com/ja-jp/azure/architecture/aws-professional/compute#containers-and-container-orchestrators)


   - サーバーレスサービス
     AWS Lambda
     Azure Functions

3. アーキテクチャ設計
   
   1. 要件の明確化
      可用性、拡張性、セキュリティ、性能などどの点を優先するか決める
   2. アーキテクチャスタイルの選択
      ７つのベストプラクティスがあるのでどれを使えばいいか選択する 

      [Azureアーキテクチャガイドまとめ Qiita](https://qiita.com/Catetin0310/items/74249f333d9fbfccd543)

      [アーキテクテャスタイル　microsoft](https://learn.microsoft.com/ja-jp/azure/architecture/guide/architecture-styles/)

   3. どのサービスを使うか検討する
   4. 10の設計原則を考慮する
   
      [Azure アプリケーションの 10 個の設計原則](https://learn.microsoft.com/ja-jp/azure/architecture/guide/design-principles/)
   5. クラウド設計パターンの適用
      クラウド特有の設計パターン（キャッシュ管理、負荷分散、冗長構成など）を活用して最適化
      [クラウド設計パターン](https://learn.microsoft.com/ja-jp/azure/architecture/patterns/)



## 使用するサービスの検討
1. Azure App ServiceかAzure Functions
   アプリケーションをデプロイして動かす環境
   処理時間の要件と課金額に併せて柔軟に変更したほうがいいかもしれない
   | -                 | App Service                                                                    | Functions                                    |
   | ----------------- | ------------------------------------------------------------------------------ | -------------------------------------------- |
   | 使用目的          | Webシステム(画面あり)やAPI(画面なし)などのサーバ上に常駐起動させるアプリに使う | バッチ処理のような短い処理を実行する際に使う |
   | AWSに相当するもの | Amazon Lightsail                                                               | Lambda                                       |
   [AWSとAzureの主要サービスの対応表](https://nokonokonetwork.com/certificate/aws/aws-and-azure-services-comparison.html)
   
   Functionsのトリガー例
   - HTTP Trigger      :HTTPリクエストを受けて関数を実行 
   - Timmer Trigger    :スケジュールで関数を実行
   - Blob Trigger      :Blobに何か追加されると関数を実行
   - Queue Trigger     :Queue Storageにメッセージが追加されると関数を実行
   - Event Hub Trigger :Event Hubにイベントが送信されると関数を実行
   - Cosmos DB Trigger : Cosmos DBの変更を検知して関数を実行


   [トリガー一覧](https://qiita.com/syantien/items/1490b2f0236133e9517f)



2. Azure Database for MySQL
   ローカルで作成したMySQLサーバの代わり

3. Azure Storage
   作成したグラフの保存場所


## 設計
マイクロサービス実装はイベントドリブンアーキテクチャで行う。

サービスが他のサービスを呼び出す方法は
①リクエスト・リプライ方式
②イベントドリブン方式
がある。
リクエスト・リプライ方式はREST APIなどを使いサービス間をつなげるが、イベントドリブン方式は、データベースへデータが格納された時などイベントを検知させることでサービスをつなげる。

proxyとskeltonのような関係で、サービスを使う側がイベントの発火がないか常に監視している。

メリットは、サービス間を疎結合させる事が可能
デメリットは、アクションがあったときにイベントが正しく発火できたかチェックしないと動作が漏れる可能性がある


イベントドリブンアーキテクチャで設計を行う
[無知から始めるイベントドリブンアーキテクチャ](https://qiita.com/Suzuki_Cecil/items/a51d353c73e9277f46d8)

