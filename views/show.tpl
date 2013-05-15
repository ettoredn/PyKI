<html>
<head>
    <title>PyKI</title>
    <style>
        input, keygen, select {
            display: block;
        }
    </style>
</head>
<body>
<h2>Certificate</h2>
<p>Download: <a href='/download/{{ serial }}/PEM'>PEM</a> <a href='download/{{ serial }}/PKCS11'>PKCS11</a></p>
<div class='certificate'><pre>{{ certificate }}</pre></div>
</body>
</html>
