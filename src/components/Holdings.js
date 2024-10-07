
const Holdings = () => {
  return (
    <div className="holdings">
      <h2>Your Holdings</h2>
      <table>
        <thead>
          <tr>
            <th>Asset</th>
            <th>Quantity</th>
            <th>Current Price</th>
            <th>Total Value</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>GOLDBEES</td>
            <td>10</td>
            <td>₹63.81</td>
            <td>₹638.10</td>
          </tr>
        </tbody>
      </table>
    </div>
  );
};

export default Holdings;
