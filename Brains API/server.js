const express = require('express');
const testroute = require('./testRoutes');
const brainsroute = require('./brainsRoute')

const app   =   express();
const port  =   3000;

    app.use('/test',testroute);
    app.use('/brains',brainsroute);

app.listen(port, () => console.log(`TiZ API listening on port ${port}!`));

