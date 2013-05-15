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
<p>
    <h3>Generate</h3>
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
    <h3>Certificates</h3>
    {% for serial in serials %}
        <div>{{ serial }}
            <a href="/download/{{ serial }}.pem">PEM</a>
            <a href="/download/{{ serial }}.cer">DER</a>
            <a href="/download/{{ serial }}.p7c">PKCS#7</a>
    {% endfor %}
</p>
<p>
    <h3>CA Commands</h3>
    <a href="/clear">Clear CA</a>
</p>
</body>
</html>
