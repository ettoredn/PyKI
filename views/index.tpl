<html>
<head>
    <title>PyKI</title>
    <style>
        input, keygen, select {
            display: block;
        }
        a:visited {
            color: blue;
        }
    </style>
</head>
<body>
<p>
    <h2>Generate</h2>
    <form action="/generate" method="post">
        <label for="type">Type:</label>
        <select name="type">
            <option value="smime">E-Mail</option>
            <option value="sslserver">Website</option>
            <option value="codesign">Code Signing</option>
        </select>
        <label for="key">Encryption</label>
        <keygen name="key" challenge="{{ challenge }}">
        <label for="dns">Website DNS</label>
        <input type="text" name="dns">
        <label for="email">E-mail</label>
        <input type="text" name="email">
        <label for="common_name">Common Name</label>
        <input type="text" name="common_name">
        <label for="organization">Organization</label>
        <input type="text" name="organization">
        <label for="locality">Locality</label>
        <input type="text" name="locality">
        <label for="country">Country</label>
        <input type="text" name="country">

        <input type="submit" value="Generate certificate">
    </form>
</p>
<p>
    <h2>Certificates</h2>
    {% for cert in certs %}
        <div>
            <span style="margin-right: 20px;">{{ cert.common_name }}</span>
            <span style="margin-right: 20px;">{{ cert.type|upper }}</span>
            <a href="/download/{{ cert.serial }}.pem">PEM</a>
            <a href="/download/{{ cert.serial }}.cer">DER</a>
            <a href="/download/{{ cert.serial }}.p7c">PKCS#7</a>
            <a href="/download/{{ cert.serial }}.p12">PKCS#12</a>
        </div>
    {% endfor %}
    <p>Password for PKCS#12 files is 'pyki'</p>
</p>
<p>
    <h2>CA Commands</h2>
    <a href="/clear">Clear CA</a>
</p>
</body>
</html>
