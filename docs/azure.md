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

      [アーキテクチャ設計参考](https://qiita.com/bluesea_nishi/items/921d1eeb2b4e3e836474)


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

1. 使用するサービスの検討


   1. ホスト先のサービス
      今回はイベントドリブンなのでAzure Functionsを選択
      [ホスティング先選定フローチャート](https://learn.microsoft.com/ja-jp/azure/architecture/guide/technology-choices/compute-decision-tree)

   2. データベース選定
      今回は将来AWSでの実装も考えているのでAzure Database for MySQLを選択
      [Azure上のデータベース](https://azure.microsoft.com/ja-jp/products/category/databases/#:~:text=%E3%82%A4%E3%83%B3%E3%83%86%E3%83%AA%E3%82%B8%E3%82%A7%E3%83%B3%E3%83%88%E3%81%A7%E7%84%A1%E5%88%B6%E9%99%90%E3%81%AE%E4%BF%A1%E9%A0%BC%E3%81%A7%E3%81%8D%E3%82%8B%E3%82%AF%E3%83%A9%E3%82%A6%E3%83%89%20%E3%83%87%E3%83%BC%E3%82%BF%E3%83%99%E3%83%BC%E3%82%B9%E3%82%92%E4%BD%BF%E7%94%A8%E3%81%97%E3%81%A6%E3%80%81%E3%82%A2%E3%83%97%E3%83%AA%E3%82%B1%E3%83%BC%E3%82%B7%E3%83%A7%E3%83%B3%E3%82%92%E6%A7%8B%E7%AF%89%E3%81%97%E3%80%81%E5%A4%89%E6%8F%9B%E3%81%97%E3%81%BE%E3%81%99%E3%80%82%20Azure%20%E3%81%A7%E3%81%AF%E3%80%81%E3%82%A2%E3%83%97%E3%83%AA%E3%82%B1%E3%83%BC%E3%82%B7%E3%83%A7%E3%83%B3%E3%81%AE%E3%83%8B%E3%83%BC%E3%82%BA%E3%81%AB%E5%90%88%E3%82%8F%E3%81%9B%E3%81%A6%E3%83%AA%E3%83%AC%E3%83%BC%E3%82%B7%E3%83%A7%E3%83%8A%E3%83%AB,%E3%83%87%E3%83%BC%E3%82%BF%E3%83%99%E3%83%BC%E3%82%B9%E3%81%A8%E9%9D%9E%E3%83%AA%E3%83%AC%E3%83%BC%E3%82%B7%E3%83%A7%E3%83%8A%E3%83%AB%20%E3%83%87%E3%83%BC%E3%82%BF%E3%83%99%E3%83%BC%E3%82%B9%E3%82%92%E9%81%B8%E6%8A%9E%E3%81%A7%E3%81%8D%E3%81%BE%E3%81%99%E3%80%82%20%E7%B5%84%E3%81%BF%E8%BE%BC%E3%81%BF%E3%81%AE%E3%82%A4%E3%83%B3%E3%83%86%E3%83%AA%E3%82%B8%E3%82%A7%E3%83%B3%E3%82%B9%E3%81%AF%E3%80%81%E9%AB%98%E5%8F%AF%E7%94%A8%E6%80%A7%E3%80%81%E3%82%B9%E3%82%B1%E3%83%BC%E3%83%AA%E3%83%B3%E3%82%B0%E3%80%81%E3%82%AF%E3%82%A8%E3%83%AA%20%E3%83%91%E3%83%95%E3%82%A9%E3%83%BC%E3%83%9E%E3%83%B3%E3%82%B9%E3%83%81%E3%83%A5%E3%83%BC%E3%83%8B%E3%83%B3%E3%82%B0%E3%81%AA%E3%81%A9%E3%81%AE%E7%AE%A1%E7%90%86%E3%82%BF%E3%82%B9%E3%82%AF%E3%82%92%E8%87%AA%E5%8B%95%E5%8C%96%E3%81%99%E3%82%8B%E3%81%AE%E3%81%AB%E5%BD%B9%E7%AB%8B%E3%81%A1%E3%81%BE%E3%81%99%E3%80%82?msockid=33b6bcaef875631c33d7a8a7f906622e)

   3. キューイングサービス
      今回の作成するサービスはユーザが少ないことと、コードの複雑化を避けるため非同期処理は使用しない為キューイングサービスも使用しない
      仮に今後ユーザが増える、もしくはLineからの応答速度が余りにも遅い場合キューイングサービスを利用し非同期処理を加えるかもしれない。（使うとしたら、ASKLLM関数の部分は外部APIを利用しているので、バックエンドでASKLLMを呼び出している間に応答処理を加えるかもしれない）

   4. グローバル負荷分散
      必要性は感じつつも、予算の関係上利用をひかえる。
      可用性向上には必要

   5. 静的コンテンツの保護
      Azure Front Door Premium で Private Link を利用することで、Azure Database for MySQLへの通信やAzure Functionsへの通信をプライベートネットワーク内に限定して、パブリックのインターネットからアクセスができなくなる。
      今回は個人情報や機密性の高い情報を使用しないので、private linkの利用は見送る


2. NWの検討
   [参考](https://qiita.com/bluesea_nishi/items/400d94915eda231a7702)
   1. VNet構成
   今回のプロジェクトは小規模の為１つのVNetにすべての機能を集約する
   中規模のプロジェクトになれば、HUB＆SPOKE構造を利用して、よく使うサービス（ファイヤーウォールやアプリケーションゲートウェイなど）をHUB VNetに配置し、その他のサービスをSPOKE VNETに配置するのがよい

   2. VNetからのアウトバウンド通信
   今回のプロジェクトでは、OpenAIのChatGPTを使用しているので設定する必要がある。
   アウトバウンド通信の許可にはAzure Firewallの設定やAzure NAT Gatewayを設定する必要がある。今回はコスト面で有利なNATを利用する
   [NATとはなにか？](https://www.bing.com/videos/riverview/relatedvideo?&q=%e3%83%8d%e3%83%83%e3%83%88%e3%83%af%e3%83%bc%e3%82%af+%e3%82%a2%e3%83%89%e3%83%ac%e3%82%b9%e5%a4%89%e6%8f%9b%e3%81%95%e3%83%bc%e3%81%b3%e3%81%99&&mid=849C74369C2335A57CF5849C74369C2335A57CF5&&mcid=ECD635B404B54BE7A48B6AD99002921E&FORM=VRDGAR)

   3. プライベート通信の実現
   VNetからAzureのPaaSサービスを使用する場合プライベートリンクやVNet統合をする必要がある。
   今回はAzure Database for MySQLを利用するので設定が必要？
   プライベートリンクはただのインターフェース。
   [プライベートリンクとは](https://www.youtube.com/watch?v=bo88q4JPOR0)
