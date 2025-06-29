const express = require('express');
const nodemailer = require('nodemailer');
const bodyParser = require('body-parser');
const cors = require('cors');
const app = express();

app.use(bodyParser.json());
app.use(cors());

app.post('/send-report', async (req, res) => {
    const { email, analysis } = req.body;

    // Email host
    const transporter = nodemailer.createTransport({
        service: 'gmail', // Replace with your email service
        auth: {
            user: 'email', // Replace with your email
            pass: 'pass' // Replace with your email password or app password
        }
    });

    const mailOptions = {
        from: 'email',
        to: email,
        subject: 'Your Report',
        html: analysis || 'No analysis provided.',
    };

    try {
        await transporter.sendMail(mailOptions);
        res.send('Report sent!');
    } catch (error) {
        console.error(error);
        res.status(500).send('Error sending email');
    }
});

app.get('/', (req, res) => {
    res.send('Email server is running!');
});

app.listen(3000, () => {
    console.log('Server running on http://localhost:3000');
});
