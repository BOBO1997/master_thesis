# IBM Quantum Washingtonでの走らせ方

## 概要

IBM Quantum Washingtonで大規模なpath graph stateを準備し、その非局所相関を計算する。

## 実行する順番

1. `cast_jobs.ipynb`: 量子回路を作成し、ジョブを実機に投げる
2. `retrieve_jobs.ipyhb`: 実機から実行結果を拾う
3. `mitigation_lnp.ipynb`: arxiv:2201.11046 のLeast Norm Filterを使ったQREM手法に従い、読み取り誤り軽減を行う
4. `analyze.ipynb`: 得られた確率分布の、Baccari et al. (arxiv:1812.10428)のBell-type不等式を使用して、非局所相関を見る

## デフォルトの設定

図のように、以下のpathを取った。

量子回路は、measurement grouping により、xzxzxzxz...基底と、zxzxzxzx...基底の2種類の回路を実行し、続いてtensor product noise modelに基づくreadout error mitigationを行うためのcalibration circuitを2つ作成する。
よって、1種類のpath graphの創刊を調べるために、以上の4つの量子回路を走らせる。
これを、path graphのサイズ `min_size = 40` から `max_size = 105` まで準備し、ひとつの　jobとして実機に投げる。
(実際この部分は、105サイズのpath graph　1つについて実行し、縮約を取るのでも同じ結果が得られるだろうと予測している。)

実機に投げたjobのjob_idはpklファイルに保存される。

実行時の時刻に対応する名前のpklファイルが生成されるため、そのファイル名を `retrieve_jobs.ipynb` で使用する。

非局所相関を計算する際には、Baccari et al.で重み付けするqubitを、`[1,4,7,11,...]` と、2つおきに設定した。