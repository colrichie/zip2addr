#!/bin/sh

######################################################################
#
# ZIP2ADDR_JSONAPI.AJAX.CGI
# 郵便番号―住所検索(よそのJSON形式Web API利用バージョン)
# Written by Rich Mikan(richmikan[at]richlab.org) at 2014/01/10
#
# [入力]
# ・[CGI変数]
#   - zipcode: 7桁の郵便番号(ハイフン無し)
# [出力]
# ・成功すればJSON形式で郵便番号、都道府県名、市区町村名、町名
# ・郵便番号辞書ファイル無し→500エラー
# ・郵便番号指定が不正      →400エラー
# ・郵便番号が見つからない  →空文字のJSONを返す
#
######################################################################


######################################################################
# 初期設定
######################################################################

# --- 変数定義 -------------------------------------------------------
dir_MINE="$(d=${0%/*}/; [ "_$d" = "_$0/" ] && d='./'; cd "$d"; pwd)" # このshのパス
readonly url_ZIPAPI='http://zipcloud.ibsnet.co.jp/api/search'        # 郵便番号辞書APIのURL(株式会社アイビス)

# --- ファイルパス ---------------------------------------------------
PATH="$(command -p getconf PATH):${PATH:-}"

# --- エラー終了関数定義 ---------------------------------------------
error500_exit() {
  cat <<-__HTTP_HEADER
	Status: 500 Internal Server Error
	Content-Type: text/plain

	500 Internal Server Error
	($@)
__HTTP_HEADER
  exit 1
}
error400_exit() {
  cat <<-__HTTP_HEADER
	Status: 400 Bad Request
	Content-Type: text/plain

	400 Bad Request
	($@)
__HTTP_HEADER
  exit 1
}


######################################################################
# メイン
######################################################################

# --- CGI変数(GETメソッド)で指定された郵便番号を取得 -----------------
zipcode=$(echo "_${QUERY_STRING:-}" | # 環境変数で渡ってきたCGI変数文字列をSTDOUTへ
          sed '1s/^_//'             | # echoの誤動作防止のために付けた"_"を除去
          tr '&' '\n'               | # CGI変数文字列(a=1&b=2&...)の&を改行に置換し、1行1変数に
          grep '^zipcode='          | # 'zipcode'という名前のCGI変数の行だけ取り出す
          sed 's/^[^=]\{1,\}=//'    | # "CGI変数名="の部分を取り除き、値だけにする
          grep '^[0-9]\{7\}$'       ) # 郵便番号の書式の正当性確認

# --- 郵便番号はうまく取得できたか？ ---------------------------------
[ -n "$zipcode" ] || error400_exit 'invalid zipcode'

# --- JSON形式文字列を生成して返す -----------------------------------
curl -s "${url_ZIPAPI}?zipcode=${zipcode}"                      | # Web APIから住所を検索し、結果をJSONで取得
tr -d '\r'                                                      | # CR+LFをLFに変換
parsrj.sh                                                       | # JSONを絶対JSONPath形式に正規化(自作プログラム)
awk '$1~/\.results\[0\]\.zipcode$/  {z = $2;}                   # # JSON中の郵便番号データを抽出
     $1~/\.results\[0\]\.address1$/ {p = $2;}                   # # JSON中の都道府県名データを抽出
     $1~/\.results\[0\]\.address2$/ {c = $2;}                   # # JSON中の市区町村名データを抽出
     $1~/\.results\[0\]\.address3$/ {t = $2;}                   # # JSON中の町名データを抽出
     END                {print z,p,c,t;}'                       | # 次コマンドに出力
awk '{print (NF==4) ? $0 : "";}'                                | # 住所が見つからなければ空行を出力する
while read zip pref city town; do                                 # HTTPヘッダーと共に、JSON文字列化した住所データを出力する
  cat <<-__HTTP_RESPONSE
	Content-Type: application/json; charset=utf-8
	Cache-Control: private, no-store, no-cache, must-revalidate
	Pragma: no-cache

	{"zip":"$zip","pref":"$pref","city":"$city","town":"$town"}
__HTTP_RESPONSE
  break
done

# --- 正常終了 -------------------------------------------------------
exit 0
