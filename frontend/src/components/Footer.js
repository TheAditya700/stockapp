import React from 'react';

const Footer = () => {
  return (
    <footer className="bg-light text-center text-lg-start mt-auto py-3">
      <div className="text-center p-3">
        © {new Date().getFullYear()} StockApp: 
        <a className="text-dark ms-1" href="/"> stockapp.com</a>
      </div>
    </footer>
  );
};

export default Footer;
