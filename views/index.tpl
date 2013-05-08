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

    <input type="submit">
</form>
</body>
</html>
