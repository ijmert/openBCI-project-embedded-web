const express = require('express')
const route = express.Router()

route.get('/hello', (req, res) => res.send('<h1>Hello World!<h1/>'));
route.get('/echo/:sometext', (req, res) => res.send(req.params.sometext));
route.post('/echo',(req,res) => {
        let temp = req.body;
        res.send(temp);
        });

module.exports = route