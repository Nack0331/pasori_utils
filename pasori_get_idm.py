# -*- coding: utf-8 -*-

from __future__ import print_function
from ctypes import *
from time import sleep

def get_idm():
    # 全NFCカードを対象とする
    # (libpafe.hの77行目で定義)
    FELICA_POLLING_ANY = 0xffff

    # ライブラリ読み込み
    libpafe = cdll.LoadLibrary("/usr/local/lib/libpafe.so")

    # PaSoRi デバイスオープン
    libpafe.pasori_open.restype = c_void_p
    pasori = libpafe.pasori_open()
    try:
        # PaSoRi 初期化
        libpafe.pasori_init(pasori)
        
        # リトライは最大3回まで
        idm_vl = 0
        for retry_cnt in range(3):
            # リクエストコマンド送信, データ受信ポーリング開始
            libpafe.felica_polling.restype = c_void_p
            felica = libpafe.felica_polling(pasori, FELICA_POLLING_ANY, 0, 0)
            try:
                # IDm 取得
                idm = c_ulonglong()
                libpafe.felica_get_idm.restype = c_void_p
                libpafe.felica_get_idm(felica, byref(idm))
                
                # IDm値を取得できた場合は値を保持しループを抜ける
                if idm.value != 0:
                    idm_vl = idm.value
                    break
            finally:
                # felica_polling()使用後はfree()を使う
                libpafe.free(felica)
                sleep(1)
        
        # 保持したIDm値を返却する
        return idm_vl
    finally:
        # オープンしたデバイスは必ずクローズする必要がある
        libpafe.pasori_close(pasori)
