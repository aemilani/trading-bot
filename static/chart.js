var chart = LightweightCharts.createChart(document.getElementById('chart'), {
	width: 1200,
    height: 600,
	layout: {
		backgroundColor: '#F9E5B5',
		textColor: '#000000',
	},
	grid: {
		vertLines: {
			color: 'rgba(197, 203, 206, 0.5)',
		},
		horzLines: {
			color: 'rgba(197, 203, 206, 0.5)',
		},
	},
	crosshair: {
		mode: LightweightCharts.CrosshairMode.Normal,
	},
	rightPriceScale: {
		borderColor: 'rgba(197, 203, 206, 0.8)',
	},
	timeScale: {
		borderColor: 'rgba(197, 203, 206, 0.8)',
	},
});

var candleSeries = chart.addCandlestickSeries({
  upColor: '#FFFFFF',
  downColor: '#000000',
  borderDownColor: '#000000',
  borderUpColor: '#000000',
  wickDownColor: '#000000',
  wickUpColor: '#000000',
});

/*fetch('http://127.0.0.1:5000/history', {mode: 'no-cors'})
	.then((r) => r.json())
	.then((response) => {
		console.log(response)
		candleSeries.setData(response);
	})*/

/*const chart = LightweightCharts.createChart(document.getElementById('chart'), { width: 1200, height: 600 });
const lineSeries = chart.addLineSeries();*/

var binanceSocket = new WebSocket('wss://stream.binance.com:9443/ws/btcusdt@trade');

/*binanceSocket.onmessage = function (event) {
    var message = JSON.parse(event.data)
    console.log(message)
    lineSeries.update({ time: message.T / 1000, value: message.p })
}*/

binanceSocket.onmessage = function (event) {
    var message = JSON.parse(event.data)
    console.log(message)
    candleSeries.update({ time: message.T / 1000, open: message.p, high: message.p, low: message.p, close: message.p })
}
