// ###################################################################
// # 共通関数
// ###################################################################

// ===== Ajaxのお約束オブジェクト作成 ================================
// [入力]
// ・なし
// [出力]
// ・成功時: XmlHttpRequestオブジェクト
// ・失敗時: false
function createXMLHttpRequest(){
  if(window.XMLHttpRequest){return new XMLHttpRequest()}
  if(window.ActiveXObject){
    try{return new ActiveXObject("Msxml2.XMLHTTP.6.0")}catch(e){}
    try{return new ActiveXObject("Msxml2.XMLHTTP.3.0")}catch(e){}
    try{return new ActiveXObject("Microsoft.XMLHTTP")}catch(e){}
  }
  return false;
}



// ###################################################################
// # 郵便番号変換関連
// ###################################################################

// ===== 郵便番号による住所検索ボタン ================================
// [入力]
// ・id="inqZipcode1"とid="inqZipcode2"の値
// [出力]
// ・指定された郵便番号に対応する住所が見つかった場合
//   - id="inqPref"な<select>の都道府県を選択
//   - id="inqCity"な<input>に市区町村名を出力
//   - id="inqTown"な<input>に町名を出力
// ・見つからなかった場合
//   - alertメッセージ
// [備考]
function zip2addr() {
  var sUrl_to_get;  // 汎用変数
  var sZipcode;     // フォームから取得した郵便番号文字列の格納用
  var xhr;          // XML HTTP Requestオブジェクト格納用
  var sUrl_ajax = 'zip2addr.ajax.cgi';  // AjaxのURL定義

  // --- 1)郵便番号を取得する ----------------------------------------
  if (! document.getElementById('inqZipcode1').value.match(/^([0-9]{3})$/)) {
    alert('郵便番号(前の3桁)が正しくありません');
    return;
  }
  sZipcode = "" + RegExp.$1;
  if (! document.getElementById('inqZipcode2').value.match(/^([0-9]{4})$/)) {
    alert('郵便番号(後の4桁)が正しくありません');
    return;
  }
  sZipcode = "" + sZipcode + RegExp.$1;


  // --- 2)Ajaxコール ------------------------------------------------
  xhr = createXMLHttpRequest();
  if (xhr) {
    sUrl_to_get  = sUrl_ajax;
    sUrl_to_get += '?zipcode='+sZipcode;
    sUrl_to_get += '&dummy='+parseInt((new Date)/1); //(*1)ブラウザcache対策

    xhr.open('GET', sUrl_to_get, true);
    xhr.onreadystatechange = function(){zip2addr_callback(xhr)};
    xhr.send(null);
  } // *1: GETメソッド時はURL文字列に、POSTメソッド時はsendの文字列につける
}
function zip2addr_callback(xhr) {

  var oAddress; // サーバーから受け取る住所オブジェクト
  var e;        // 汎用変数(エレメント用)

  // --- 3)アクセス成功で呼び出されたのでないなら即終了 --------------
  if (xhr.readyState != 4) {return;}
  if (xhr.status == 0    ) {return;} // ステータスが0の場合はクライアントによる中断の可能性があるので無視
  if      (xhr.status == 400) {
    alert('郵便番号が正しくありません');
    return;
  }
  else if (xhr.status != 200) {
    alert('アクセスエラー(' + xhr.status + ')');
    return;
  }

  // --- 4)サーバーから返された住所データを格納 ----------------------
  oAddress =  JSON.parse(xhr.responseText);
  if (oAddress['zip'] === '') {
    alert('対応する住所が見つかりませんでした');
    return;
  }

  // --- 5)都道府県名を選択する --------------------------------------
  e = document.getElementById('inqPref')
  for (var i=0; i<e.options.length; i++) {
    if (e.options.item(i).value == oAddress['pref']) {
      e.selectedIndex = i;
      break;
    }
  }

  // --- 6)市区町村名を流し込む --------------------------------------
  document.getElementById('inqCity').value = oAddress['city'];

  // --- 7)町名を流し込む --------------------------------------------
  document.getElementById('inqTown').value = oAddress['town'];

  // --- 99)正常終了 -------------------------------------------------
  return;
}
