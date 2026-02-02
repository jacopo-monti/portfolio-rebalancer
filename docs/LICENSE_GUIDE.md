# GNU AGPL v3 License Guide

Portfolio Rebalancer is licensed under the **GNU Affero General Public License v3.0 or later (AGPL-3.0-or-later)**.

This document explains what you can and cannot do with this software.

---

## ✅ What You CAN Do

### Personal Use
- ✅ Use the software privately without any restrictions
- ✅ Modify the code for personal use
- ✅ Study and read the source code
- ✅ Test and experiment with the software
- ✅ Run it locally on your computer or servers

### Distribution and Contribution
- ✅ Share the software with others (unchanged or modified)
- ✅ Create your own version (fork) and distribute it
- ✅ Use it in commercial projects (with conditions below)
- ✅ Sell the software (but keep AGPL license)
- ✅ Contribute improvements back to the community
- ✅ Create derivative works and enhancements
- ✅ Use it in web applications and SaaS (with conditions below)

### Commercial Use
- ✅ Use it internally in your company for free (private use)
- ✅ Offer services built on top of this software
- ✅ Charge for consulting, customization, or support
- ✅ Create a commercial SaaS product using this code
- ✅ Sell modified versions of the software

---

## ❌ What You CANNOT Do

### Closed Source / Proprietary
- ❌ Make the code proprietary or closed-source
- ❌ Incorporate this code into a closed-source software project
- ❌ Remove or hide the original copyright notices
- ❌ Change the license to something more permissive
- ❌ Create a proprietary fork that you don't share

### Web Applications (AGPL Specific)
- ❌ Run a SaaS service without publishing your modified source code
- ❌ Use this in a web application and hide the modifications from users
- ❌ Hide the fact that you're using this software on your server

### Distribution Without Source
- ❌ Distribute modified versions without providing source code access
- ❌ Distribute without including a copy of the AGPL-3.0 license
- ❌ Distribute without documenting what changes you made
- ❌ Distribute in binary-only form without offering source code

### Liability
- ❌ Hold the authors liable for software defects or damages
- ❌ Claim any warranty or guarantee about the software's functionality

---

## 📊 Use Case Matrix

| Use Case | Allowed? | Conditions |
|----------|----------|------------|
| **Personal/Private Use** | ✅ Yes | None |
| **Modify for Personal Use** | ✅ Yes | None |
| **Internal Company Use** | ✅ Yes | None (it's private use) |
| **Share Unmodified Code** | ✅ Yes | Include license and copyright |
| **Share Modified Code** | ✅ Yes | Must be AGPL-3.0, document changes |
| **Distribute as-is** | ✅ Yes | Include LICENSE file and notices |
| **Create a Fork** | ✅ Yes | Must remain AGPL-3.0 |
| **Use in Desktop Application** | ✅ Yes | If distributed, provide source code |
| **Use in Web Application** | ✅ Yes | Must provide source code to users |
| **Commercial Internal Use** | ✅ Yes | No restrictions (private) |
| **Offer Commercial Services** | ✅ Yes | Can charge for services/support |
| **Sell Modified Software** | ✅ Yes | License must remain AGPL-3.0 |
| **Create Proprietary Fork** | ❌ No | Copyleft prevents this |
| **Use in Closed-Source Project** | ❌ No | Copyleft prevents this |
| **Run SaaS Without Publishing Code** | ❌ No | AGPL requires source disclosure |
| **Remove Copyright Notices** | ❌ No | Illegal |
| **Change License Unilaterally** | ❌ No | You don't have this right |
| **Claim Warranty** | ❌ No | Software provided as-is |

---

## 🔍 Real-World Examples

### ✅ ALLOWED: Personal Use
```
You download portfolio-rebalancer and use it to rebalance your own portfolio.
→ Status: ✅ ALLOWED (no obligations)
```

### ✅ ALLOWED: Internal Company Use
```
Your company uses portfolio-rebalancer internally to manage client portfolios.
→ Status: ✅ ALLOWED (no obligations, it's private use)
```

### ✅ ALLOWED: Modify and Improve
```
You modify the code to add new features and publish your version on GitHub.
→ Status: ✅ ALLOWED
→ Requirement: Must be licensed as AGPL-3.0 and include change documentation
```

### ✅ ALLOWED: Charge for Services
```
You offer consulting services to help users implement portfolio-rebalancer.
→ Status: ✅ ALLOWED (you charge for service, not the software itself)
```

### ✅ ALLOWED: SaaS with Open Source Code
```
You create a web application using portfolio-rebalancer, host it online,
and publish your modified source code on GitHub under AGPL-3.0.
→ Status: ✅ ALLOWED
→ Requirement: Users must have access to the source code
```

### ✅ ALLOWED: Sell the Software
```
You distribute portfolio-rebalancer (modified or not) and charge €50 per copy.
→ Status: ✅ ALLOWED
→ Requirement: Buyers receive source code and AGPL license
```

### ❌ NOT ALLOWED: Closed-Source SaaS
```
You create a web application using portfolio-rebalancer and offer it online,
but you don't publish your source code.
→ Status: ❌ NOT ALLOWED
→ Reason: AGPL v3 (unlike GPL v3) requires source disclosure for network use
```

### ❌ NOT ALLOWED: Proprietary Fork
```
You fork portfolio-rebalancer, modify it extensively, and sell it as a
closed-source product under your own company branding.
→ Status: ❌ NOT ALLOWED
→ Reason: Copyleft prevents creating proprietary derivatives
```

### ❌ NOT ALLOWED: Closed-Source Incorporation
```
You incorporate portfolio-rebalancer into your commercial software product
and distribute it without source code.
→ Status: ❌ NOT ALLOWED
→ Reason: Copyleft prohibits this
```

### ❌ NOT ALLOWED: Hide Source Code in SaaS
```
You use portfolio-rebalancer in your web application and claim it's your
own proprietary technology, without publishing modifications.
→ Status: ❌ NOT ALLOWED
→ Reason: AGPL v3 requires source code availability for network services
```

---

## 🔄 AGPL v3 vs GPL v3: Key Difference

The most important difference between AGPL v3 and GPL v3:

### GPL v3
- Copyleft applies only when you **distribute** the software
- If you use it on your own server without distributing it → no obligation
- This is called the "server loophole"

### AGPL v3
- Copyleft applies when you **distribute** the software
- **AND** when you use it over a network (SaaS, web app, API)
- No "server loophole" – source code must be available to users

**Implication for Portfolio-Rebalancer:**

If you use it in a SaaS product or web application:
- 📋 **GPL v3**: No obligation (could keep source private)
- 📋 **AGPL v3**: Must provide source code to users

---

## 💼 Commercial Strategies

### Strategy 1: Open Source + Services
```
Distribute the software free under AGPL-3.0
Monetize with:
  • Professional services & consulting
  • Training and workshops
  • Premium support plans
  • Customization services
```

### Strategy 2: Dual Licensing
```
Offer two licenses:
  1. AGPL-3.0 for open-source users (free)
  2. Commercial license for closed-source use (paid)
  
Note: As the copyright holder, you (the author) can do this.
Other contributors cannot.
```

### Strategy 3: SaaS with Open Source Code
```
Create a web application using the software
Publish your modifications under AGPL-3.0
Monetize with:
  • Hosting and infrastructure
  • User-friendly interface
  • Premium features
  • Data storage and backups
```

### Strategy 4: Enhanced Commercial Product
```
Create an enhanced version with additional features
Offer both:
  1. Free AGPL-3.0 base version
  2. Paid commercial version with extras
```

---

## 📋 Compliance Checklist

If you distribute portfolio-rebalancer or create derivatives:

### For All Distributions
- [ ] Include the full text of the GNU AGPL v3 license
- [ ] Include the original copyright notice(s)
- [ ] Document all modifications you made
- [ ] Provide clear attribution to original authors

### For Modified Versions
- [ ] Document what changes you made and when
- [ ] Add your copyright notice (you own your modifications)
- [ ] Keep the AGPL-3.0 license on the entire work
- [ ] Make source code available to recipients

### For Web Applications / SaaS
- [ ] Provide users with access to the modified source code
- [ ] Include a link to download the source code
- [ ] Document your modifications clearly
- [ ] Make the source code available in a timely manner

### For Distributed Binaries
- [ ] Include license and copyright notices
- [ ] Offer to provide source code (in writing or online)
- [ ] Document modifications
- [ ] Make source code reasonably accessible

---

## ⚖️ Legal Notes

### Warranty Disclaimer
The software is provided "AS-IS" without warranty of any kind:
- No warranty of merchantability
- No warranty of fitness for a particular purpose
- No warranty of non-infringement
- Authors are not liable for damages

### Your Rights
As long as you follow the license terms:
- You have unlimited rights to use, modify, and distribute
- The license is perpetual (doesn't expire)
- The license is worldwide
- The license is royalty-free (no payments required)

### Enforcement
- Copyright holders can enforce the license
- Violations can result in legal action
- Compliance is your responsibility

---

## 🔗 Additional Resources

- **Full License Text**: [LICENSE](../LICENSE) file in this repository
- **Official GNU AGPL v3**: https://www.gnu.org/licenses/agpl-3.0.html
- **AGPL Explained**: https://www.gnu.org/licenses/agpl-3.0-standalone.html
- **Choose a License**: https://choosealicense.com/licenses/agpl-3.0/
- **SPDX License**: https://spdx.org/licenses/AGPL-3.0-or-later.html

---

## ❓ Still Unsure?

If your use case is not covered here, consider:

1. **Consulting a lawyer** – if it's important for your business
2. **Asking the maintainers** – we can clarify intent or discuss dual licensing
3. **Reviewing the full license** – read the LICENSE file for precise legal language

**Remember**: When in doubt, keeping the code open-source under AGPL-3.0 is always safe! 🎯
