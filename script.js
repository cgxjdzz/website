function sendRequest() {
    // 获取输入框中的数据
    var inputData = document.getElementById("input_data").value;
  
    // 创建XMLHttpRequest对象
    var xhr = new XMLHttpRequest();
  
    // 配置请求
    xhr.open("POST", "/api");
  
    // 设置请求头部
    xhr.setRequestHeader("Content-Type", "application/xml");
  
    // 处理响应
    xhr.onreadystatechange = function() {
      if (xhr.readyState === XMLHttpRequest.DONE) {
        if (xhr.status === 200) {
          // 解析响应
          var parser = new DOMParser();
          var xmlDoc = parser.parseFromString(xhr.responseText, "text/xml");
          var outputData = xmlDoc.getElementsByTagName("output_data")[0].childNodes[0].nodeValue;
  
          // 将响应写入输出框中
          document.getElementById("output_data").value = outputData;
        } else {
          // 请求失败，输出错误信息
          console.log("Error: " + xhr.status);
        }
      }
    };
  
    // 发送请求
    xhr.send(inputData);
  }