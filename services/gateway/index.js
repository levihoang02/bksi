const http = require('http');
const app = require('./app');
const dotenv = require('dotenv');
const sequelize = require('./services/database');
const config= require ('./config')();
const initialize = require('./initialize');

sequelize.sync({ force: false }).then(() => {
    console.log('Database is ready');
    initialize().then(()=> {
        console.log("Finish initalize gateway");
        dotenv.config();
    
        const PORT = config.gateway.port || 3000;
    
        const sever = http.createServer(app);
    
        sever.listen(PORT, () => {
            console.log(`Server is running on port ${PORT}`);
        });
    });
});
