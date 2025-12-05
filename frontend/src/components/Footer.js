import React from 'react';

const Footer = () => {
  return (
    <footer className="bg-dark-cyan text-center text-white mt-auto py-3">
      <div className="text-center p-3">
        © {new Date().getFullYear()} StockStock: 
        <a className="text-white ms-1" href="https://github.com/TheAditya700"> Aditya Hriday Rath</a>
      </div>
    </footer>
  );
};

export default Footer;
