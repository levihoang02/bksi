const http = require('http');
const app = require('./app');
const dotenv = require('dotenv');

dotenv.config();

const PORT = process.env.PORT || 3000;

const sever = http.createServer(app);

sever.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
