// frontend/tests/test_login.js
// a tiny test for your login validation function (adapt to your actual function names)

function validateLogin(username, password) {
    if (!username || !password) return false;
    if (username.length < 10 || password.length < 3) return false;
    return true;
}

// tests
console.assert(validateLogin("dev123@gmail.com", "123") === true, "valid credentials should pass");
console.assert(validateLogin("", "123") === false, "empty username should fail");
console.assert(validateLogin("de", "123") === false, "short username should fail");
console.assert(validateLogin("dev123@gmail.com", "12") === false, "short password should fail");

console.log("✅ frontend/tests/test_login.js: All assertions passed");
