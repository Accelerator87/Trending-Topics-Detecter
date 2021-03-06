# PTT竄紅話題偵測系統

## 介紹
一個能夠在指定分類、指定時段中，偵測出當時在PTT中的竄紅之話題的系統。

## 優點
1. 對「話題」做一個客觀且完整的定義，並準確分析出竄紅的話題，最後依據不同話題的竄紅程度排名。
2. 依據使用者不同的需求，在使用者自訂的話題分類以及自訂的一段時間中，找出曾經在短時間內被大量的討論的話題。
3. 我們設計了一個簡單的UI介面，並將結果以折線圖的方式呈現，使大部分沒有程式基礎的民眾都能夠輕鬆地使用。

## 使用步驟
1. 先以以下指令下載一個叫做 jieba 的 Python Package 。
```python=
pip install jieba
```
2. 下載ptt.py及stopwords.txt，並放在同一個資料夾中。
3. 執行ptt.py後，會出現一個UI介面。
4. 在這個介面中自訂自己所要查詢的時間範圍、看板等。
5. 自訂完成後按下送出，程式會根據自訂的內容，偵測出竄紅話題，並繪製出出現分布折線圖後將此圖表存檔。
