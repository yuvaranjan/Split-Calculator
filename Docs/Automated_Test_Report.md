# Split Calculator: Automated Edge Case Test Report

I successfully executed an automated headless suite against your core JavaScript application logic (`app.js`) mimicking a browser DOM environment. As requested, **no modifications were made to your scripts or local database state**.

Here is the finalized end report detailing how your application's logic responded to the targeted stress tests, followed by recommended improvements.

---

## 🧪 Test Execution Results

### 1. Mathematical & Logic Core
* **The 1/3 Rounding Problem (₹100 among 3 people):** ✅ **Passed**
  * *Result:* The engine uses native double-precision floats under the hood (allocating `33.333333333333336` to each person). Because JS floats preserve this precision, the sums reconstruct perfectly to `100` preventing any strict validation crashes.
* **Zero-Value Inputs (₹0.00 expense):** ✅ **Passed**
  * *Result:* The system safely halted execution prior to any divide-by-zero operations, correctly throwing the validation message: *"Add a description, amount, and at least one person."*
* **Data Type Overflows (₹9,999,999.00 expense):** ✅ **Passed**
  * *Result:* The database smoothly parsed the massive integer. Visually, your CSS grid paired with `.activity-title` (`white-space: nowrap`, `overflow: hidden`, `text-overflow: ellipsis`) successfully prevented any layout clutter or DOM breaking.

### 2. Unequal & Complex Splits
* **The Non-Participant Payer (A pays ₹300, only B & C split):** ✅ **Passed**
  * *Result:* Net balances were updated with mathematical accuracy. Person A became a +300 creditor, while B and C successfully inherited -150 debts.
* **Mismatched Exact Totals (₹450 assigned on a ₹500 bill):** ✅ **Passed**
  * *Result:* The form blocked submission successfully, returning the exact validation error: *"Exact shares must add up to ₹500.00."*
* **The Zero-Share Participant (0% assigned to a participant):** ✅ **Passed**
  * *Result:* Logic cleanly assigned ₹0.00 to the disabled participant and redistributed the remaining financial burden evenly across the active percentage assignments without throwing a `NaN` error.

### 3. Reimbursement Anomalies
* **Overpayment (₹200 paid to settle a ₹100 debt):** ✅ **Passed**
  * *Result:* The ledger intelligently registered the over-transfer, seamlessly flipping the debtor into a net-creditor (+100) and moving the initial creditor into negative standing (-100).
* **Cyclic Debt Settlement (A owes B ₹100, B owes C ₹100, C owes A ₹100):** ✅ **Passed**
  * *Result:* Your `settlements()` algorithm perfectly identified the circular loop. The resulting generated settlements list simplified to exactly `0` suggested moves. 

### 4. Minimal UI & State Resilience
* **Whitespace & Clutter Constraints (Excessively long title):** ✅ **Passed**
  * *Result:* String manipulation and CSS boundaries correctly truncated the title string with an ellipsis.
* **Background State Preservation (App backgrounded during data entry):** ❌ **Failed**
  * *Result:* The `app.js` architecture strictly triggers `saveState()` only on the final form submission. If the OS unloads the WebView/Activity memory while answering a phone call, all partially filled complex multi-item input fields are permanently wiped.

---

## 🛠️ Suggested Changes (Actionable Feedback)

As requested, I did not implement these changes on my own, but I highly recommend making the following adjustments to your logic:

1. **Implement Draft Auto-Saving (Fix for Background State Resilience):**
   * *The Issue:* Entering large exact/percentage splits takes time, and losing it to a phone call is frustrating.
   * *The Fix:* Add a `visibilitychange` or `pagehide` event listener to `document` that serializes the current form values (description, amount, shares) into a temporary `localStorage` key (e.g., `splitwise-draft`). On app load, check for this key and restore the form fields if it exists.
2. **Handle Real-World Penny Distribution (Enhancement for Rounding):**
   * *The Issue:* While the application logic doesn't crash on `100 / 3`, the generated internal shares are infinite decimals (`33.333333...`). If these get pushed to a CSV export, the floating points look messy and unrealistic for real currency.
   * *The Fix:* In `addExpense` (under the `shareType === 'equal'` block), force rounding to exactly two decimal places using `Math.round(each * 100) / 100`. Add any missing remainder pennies (e.g., the missing ₹0.01) explicitly to the first participant's (or payer's) share to guarantee the currency cleanly totals the receipt amount. 
3. **Restrict Negative Amount Submissions in Share Inputs:**
   * *The Issue:* Although you block zero-value main totals, users can technically type `-50` into an individual "exact" share input field (if they bypass the HTML `min="0"` constraint).
   * *The Fix:* In your `addExpense` exact/percentage validation loop, add a rigid JavaScript condition asserting that `value >= 0` for all share inputs.
