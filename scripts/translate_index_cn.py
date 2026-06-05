#!/usr/bin/env python3
r"""Translate makeindex output (.ind) terms into Chinese for hott-book-cn.

Strategy:
- Parse visible index terms from `\item/\subitem/\subsubitem` lines.
- Translate terms using:
  1) strict terminology mapping from TERMINOLOGY_CN.md
  2) curated extra phrase mappings
  3) fallback word-level mapping
- Preserve TeX commands/math and page-reference payloads.
- Translate `\see{...}` / `\seealso{...}` targets consistently.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def normalize_key(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def load_term_table(md: Path) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for line in md.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\|\s*(.*?)\s*\|\s*(.*?)\s*\|", line)
        if not m:
            continue
        en = m.group(1).strip().strip("`")
        zh = m.group(2).strip().strip("`")
        if not en or en in {"English term", "---"}:
            continue
        if not re.search(r"[A-Za-z]", en):
            continue
        zh = re.sub(r"（[^）]*）", "", zh).strip()
        if zh:
            mapping[normalize_key(en)] = zh
    return mapping


# Phrase-level overrides (sorted longest-first later).
EXTRA_PHRASE: Dict[str, str] = {
    "index of symbols": "符号索引",
    "proof assistant": "证明助手",
    "homotopy-initial": "同伦初始",
    "model category": "模型范畴",
    "groupoid model": "群胚模型",
    "quillen model category": "Quillen 模型范畴",
    "hom-set": "态射集",
    "path constructor": "路径构造子",
    "point constructor": "点构造子",
    "based path induction": "基路径归纳",
    "path induction": "路径归纳",
    "iterated loop space": "迭代回路空间",
    "loop space": "回路空间",
    "cartesian product": "笛卡尔积",
    "smash product": "挤压积",
    "wedge": "楔和",
    "pushout": "余推",
    "pullback": "拉回",
    "epimorphism": "满态射",
    "monomorphism": "单态射",
    "surjection": "满射",
    "injection": "单射",
    "2-dimensional": "二维",
    "3-dimensional": "三维",
    "n-dimensional": "n维",
    "2-out-of-3 property": "2-out-of-3 性质",
    "2-out-of-6 property": "2-out-of-6 性质",
    "non-hypercomplete": "非超完备",
    "type-theoretic axiom of choice": "类型论的选择公理",
    "function extensionality": "函数外延性",
    "propositional truncation": "命题截断",
    "equivalence relation": "等价关系",
    "identity type": "恒等类型",
    "univalence axiom": "泛等公理",
    "univalence": "泛等",
    "univalent foundations": "泛等基础",
    "homotopy type theory": "同伦类型论",
    "type theory": "类型论",
    "set theory": "集合论",
    "category of sets": "集合范畴",
    "fundamental groupoid": "基本群胚",
    "fundamental group": "基本群",
    "fundamental pregroupoid": "基本预群胚",
    "topological space": "拓扑空间",
    "ordered field": "有序域",
    "cauchy reals": "Cauchy 实数",
    "dedekind reals": "Dedekind 实数",
    "natural numbers": "自然数",
    "real numbers": "实数",
    "rational numbers": "有理数",
    "ordinal numbers": "序数",
    "integers": "整数",
    "empty type": "空类型",
    "unit type": "单元类型",
    "coproduct type": "余积类型",
    "dependent pair type": "依值配对类型",
    "dependent function type": "依值函数类型",
    "connected function": "连通函数",
    "truncated function": "截断函数",
    "connected": "连通",
    "truncated": "截断",
    "inductive": "归纳",
    "admissible": "可容许",
    "action": "作用",
    "addition": "加法",
    "adjoint": "伴随",
    "absolute value": "绝对值",
    "acceptance": "接受",
    "algorithm": "算法",
    "continuity": "连续性",
    "inductive-inductive": "归纳-归纳",
    "inductive-recursive": "归纳-递归",
    "homotopy-inductive": "同伦归纳",
    "uniqueness": "唯一性",
    "truth": "真值",
    "abstract stone duality": "抽象 Stone 对偶",
    "double negation": "双重否定",
    "double negation axiom": "双重否定公理",
    "double negation law": "双重否定律",
    "de morgan's laws": "de Morgan 律",
    "de morgan law": "de Morgan 律",
    "blakers--massey theorem": "Blakers--Massey 定理",
    "diaconescu's theorem": "Diaconescu 定理",
    "feit--thompson theorem": "Feit--Thompson 定理",
    "four-color theorem": "四色定理",
    "freudenthal suspension theorem": "Freudenthal 悬挂定理",
    "hedberg's theorem": "Hedberg 定理",
    "schroeder--bernstein theorem": "Schroeder--Bernstein 定理",
    "whitehead's principle": "Whitehead 原理",
    "van kampen theorem": "van Kampen 定理",
    "eckmann--hilton argument": "Eckmann--Hilton 论证",
    "eilenberg--mac lane space": "Eilenberg--Mac Lane 空间",
    "fubini theorem for colimits": "余极限的 Fubini 定理",
    "grothendieck construction": "Grothendieck 构造",
    "hopf fibration": "Hopf 纤维化",
    "klein bottle": "Klein 瓶",
    "lawvere-tierney": "Lawvere-Tierney",
    "lawvere-tierney operator": "Lawvere-Tierney 算子",
    "lawvere-tierney topology": "Lawvere-Tierney 拓扑",
    "five stages of accepting constructive mathematics": "接受构造性数学的五个阶段",
    "accepting constructive mathematics": "接受构造性数学",
    "pointfree": "无点",
    "set-theoretic": "集合论的",
    "set-coequalizer": "集合余等化子",
    "set-pushout": "集合余推",
    "factorization system": "分解系统",
    "identity proofs": "恒等证明",
    "recursive definition": "递归定义",
    "subsingleton": "亚单例",
    "natural transformation": "自然变换",
    "non-dependent": "非依值",
    "type-theoretic": "类型论的",
    "impredicative": "非直谓",
    "predicative": "直谓",
    "non-expanding": "非扩张",
    "pseudo-ordinal": "伪序数",
    "bool, nonidentity": "$\\bool$ 的非恒等",
}


# Word-level fallback mapping.
WORD: Dict[str, str] = {
    "of": "的",
    "for": "的",
    "in": "中",
    "on": "上",
    "to": "到",
    "by": "由",
    "with": "与",
    "under": "下",
    "over": "上",
    "between": "之间",
    "from": "从",
    "into": "到",
    "as": "作",
    "and": "和",
    "or": "或",
    "not": "非",
    "a": "",
    "an": "",
    "the": "",
    "type": "类型",
    "types": "类型",
    "theory": "理论",
    "function": "函数",
    "functions": "函数",
    "dependent": "依值",
    "numbers": "数",
    "number": "数",
    "path": "路径",
    "paths": "路径",
    "group": "群",
    "groups": "群",
    "groupoid": "群胚",
    "groupoids": "群胚",
    "space": "空间",
    "spaces": "空间",
    "functor": "函子",
    "functors": "函子",
    "theorem": "定理",
    "lemma": "引理",
    "corollary": "推论",
    "definition": "定义",
    "remark": "注记",
    "example": "例",
    "exercise": "练习",
    "product": "积",
    "principle": "原理",
    "relation": "关系",
    "relations": "关系",
    "identity": "恒等",
    "equality": "相等",
    "map": "映射",
    "maps": "映射",
    "set": "集合",
    "sets": "集合",
    "induction": "归纳",
    "higher": "高阶",
    "dimensional": "维",
    "field": "域",
    "rule": "规则",
    "rules": "规则",
    "modality": "模态",
    "pair": "配对",
    "family": "类型族",
    "algebra": "代数",
    "truncation": "截断",
    "truncated": "截断",
    "metric": "度量",
    "coproduct": "余积",
    "constructor": "构造子",
    "constructors": "构造子",
    "cover": "覆盖",
    "cardinal": "基数",
    "linear": "线性",
    "ordered": "有序",
    "free": "自由",
    "algebraic": "代数",
    "mathematics": "数学",
    "propositional": "命题",
    "proposition": "命题",
    "propositions": "命题",
    "subset": "子集",
    "subsets": "子集",
    "cartesian": "笛卡尔",
    "homotopy": "同伦",
    "homotopies": "同伦",
    "logic": "逻辑",
    "interval": "区间",
    "continuous": "连续",
    "system": "系统",
    "suspension": "悬垂",
    "property": "性质",
    "ordinal": "序数",
    "surreal": "超现实",
    "surreals": "超现实数",
    "monoid": "幺半群",
    "choice": "选择",
    "completion": "完备化",
    "real": "实",
    "reals": "实数",
    "sphere": "球面",
    "point": "点",
    "surjective": "满射",
    "application": "应用",
    "constant": "常值",
    "loop": "回路",
    "homomorphism": "同态",
    "mere": "纯",
    "merely": "仅可",
    "pre": "预",
    "precategory": "预范畴",
    "structure": "结构",
    "structures": "结构",
    "notation": "记号",
    "classical": "经典",
    "constructive": "构造性",
    "concatenation": "拼接",
    "semigroup": "半群",
    "axiom": "公理",
    "universe": "宇宙",
    "universes": "宇宙",
    "univalence": "泛等",
    "isomorphism": "同构",
    "isomorphic": "同构",
    "closed": "封闭",
    "sequence": "序列",
    "decidable": "可判定",
    "fiberwise": "逐纤维",
    "adjoint": "伴随",
    "essentially": "本质",
    "fiber": "纤维",
    "uniformly": "一致",
    "cumulative": "累积",
    "topological": "拓扑",
    "order": "序",
    "unitary": "酉",
    "morphism": "态射",
    "morphisms": "态射",
    "disjoint": "不交",
    "categories": "范畴",
    "category": "范畴",
    "polynomial": "多项式",
    "hypothesis": "假设",
    "approximation": "逼近",
    "approximations": "逼近",
    "composition": "复合",
    "negation": "否定",
    "extensionality": "外延性",
    "resizing": "缩放",
    "collection": "汇集",
    "quantifier": "量词",
    "locally": "局部",
    "complex": "复形",
    "circle": "圆",
    "class": "类",
    "exact": "正合",
    "booleans": "布尔",
    "identities": "恒等",
    "proof": "证明",
    "intervals": "区间",
    "universal": "泛",
    "hierarchy": "层级",
    "cut": "分割",
    "recursion": "递归",
    "rational": "有理",
    "empty": "空",
    "logical": "逻辑",
    "weak": "弱",
    "pullback": "拉回",
    "faithful": "忠实",
    "fibration": "纤维化",
    "invertible": "可逆",
    "image": "像",
    "images": "像",
    "split": "分裂",
    "bounded": "有界",
    "pushout": "余推",
    "fundamental": "基本",
    "abstraction": "抽象",
    "basepoint": "基点",
    "adjunction": "伴随",
    "conversion": "转换",
    "apartness": "分离关系",
    "coherence": "相干性",
    "list": "列表",
    "lists": "列表",
    "extensional": "外延",
    "well-founded": "良基",
    "excluded": "排中",
    "middle": "中律",
    "strong": "强",
    "based": "基",
    "bi-invertible": "双可逆",
    "topos": "拓扑斯",
    "variable": "变量",
    "simulation": "模拟",
    "inequality": "不等式",
    "analysis": "分析",
    "complete": "完备",
    "opposite": "对偶",
    "slice": "切片",
    "term": "项",
    "definitional": "定义",
    "matching": "匹配",
    "structural": "结构",
    "eliminator": "消去子",
    "embedding": "嵌入",
    "contractible": "可缩",
    "full": "满",
    "pointed": "带点",
    "colimit": "余极限",
    "quotient": "商",
    "predicate": "谓词",
    "inhabited": "可居留",
    "open": "开",
    "unit": "单位",
    "kernel": "核",
    "upper": "上",
    "inverse": "逆",
    "level": "层级",
    "positive": "正",
    "substitution": "代换",
    "abelian": "阿贝尔",
    "language": "语言",
    "accessibility": "可达性",
    "adjoining": "伴随添加",
    "cell": "胞腔",
    "colimits": "余极限",
    "initial": "初始",
    "amalgamated": "并合",
    "archimedean": "阿基米德",
    "limited": "有限",
    "omniscience": "全知",
    "separation": "分离",
    "countable": "可数",
    "replacement": "替代",
    "octahedral": "八面体",
    "versus": "对比",
    "bracket": "括号",
    "exponentiation": "指数",
    "cocomplete": "余完备",
    "regular": "正则",
    "skeletal": "骨架",
    "strict": "严格",
    "completeness": "完备性",
    "operator": "算子",
    "separable": "可分",
    "small": "小",
    "object": "对象",
    "subobject": "子对象",
    "cocone": "余锥",
    "codomain": "陪域",
    "coequalizer": "余等化子",
    "cofiber": "余纤维",
    "stack": "层叠",
    "computation": "计算",
    "pairs": "配对",
    "assistant": "助手",
    "arithmetic": "算术",
    "primitive": "原始",
    "constructivity": "构造性",
    "context": "上下文",
    "contradiction": "矛盾",
    "contravariant": "反变",
    "convertibility": "可转换性",
    "covariant": "协变",
    "pointwise": "逐点",
    "currying": "柯里化",
    "cyclic": "循环",
    "deductive": "演绎",
    "equation": "方程",
    "pattern": "模式",
    "descent": "下降",
    "sum": "和",
    "dummy": "哑",
    "dyadic": "二元",
    "argument": "论证",
    "elimination": "消去",
    "end": "端",
    "epimorphism": "满态射",
    "heterogeneous": "异质",
    "judgmental": "判断",
    "equals": "相等",
    "half": "半",
    "expansion": "展开",
    "existential": "存在",
    "extended": "扩展",
    "local": "局部",
    "stability": "稳定性",
    "basic": "基本",
    "transformation": "变换",
    "approximate": "近似",
    "foundations": "基础",
    "fully": "全",
    "section": "截面",
    "representable": "可表",
    "equivalence": "等价",
    "equivalences": "等价",
    "synthetic": "综合",
    "operad": "operad",
    "construction": "构造",
    "limit": "极限",
    "spoke": "辐条",
    "triangle": "三角",
    "zigzag": "锯齿",
    "encoding": "编码",
    "torus": "环面",
    "vectors": "向量",
    "segment": "段",
    "law": "律",
    "intuitionistic": "直觉主义",
    "lattice": "格",
    "abuse": "滥用",
    "bound": "界",
    "vs": "对比",
    "fold": "折叠",
    "lower": "下",
    "mapping": "映射",
    "proof-relevant": "证明相关",
    "membership": "隶属",
    "mistaken": "误用",
    "mutual": "互",
    "encoded": "编码",
    "non-strict": "非严格",
    "classifier": "分类子",
    "subterminal": "亚终对象",
    "odd-order": "奇阶",
    "weakly": "弱地",
    "admissible": "可容许",
    "plump": "丰满",
    "trichotomy": "三歧",
    "parallel": "平行",
    "start": "起点",
    "pretopos": "预拓扑斯",
    "positivity": "正性",
    "uniqueness": "唯一性",
    "word": "词",
    "subuniverse": "子宇宙",
    "separated": "分离",
    "rewriting": "重写",
    "ring": "环",
    "simply": "简单",
    "squash": "压扁",
    "notion": "概念",
    "formal": "形式",
    "unintentional": "无意",
    "truth": "真值",
    "absolute": "绝对",
    "value": "值",
    "abstract": "抽象",
    "duality": "对偶",
    "acceptance": "接受",
    "accessible": "可达",
    "adjective": "形容词",
    "adverb": "副词",
    "endofunctor": "内自函子",
    "algorithm": "算法",
    "analytic": "分析",
    "anger": "愤怒",
    "arity": "元数",
    "arrow": "箭头",
    "associativity": "结合性",
    "operation": "运算",
    "assumption": "假设",
    "fixed-point-free": "无不动点",
    "nonidentity": "非恒等",
    "theoretic": "理论",
    "unique": "唯一",
    "infinity": "无穷",
    "reducibility": "可约性",
    "generalization": "推广",
    "bargaining": "议价",
    "reduction": "约化",
    "bimodule": "双模",
    "bisimulation": "双模拟",
    "bit": "位",
    "bitotal": "双全",
    "totally": "全序地",
    "capture": "捕获",
    "addition": "加法",
    "multiplication": "乘法",
    "cardinality": "基数",
    "center": "中心",
    "discrete": "离散",
    "well-pointed": "良基点",
    "caves": "洞穴",
    "walls": "墙",
    "contraction": "收缩",
    "chaotic": "混沌",
    "codes": "编码",
    "coercion": "强制转换",
    "raising": "提升",
    "cohomology": "上同调",
    "coincidence": "重合",
    "square": "方块",
    "comonad": "余单子",
    "compactness": "紧致性",
    "complement": "补集",
    "component": "分量",
    "horizontal": "水平",
    "computational": "计算性",
    "effect": "效应",
    "computer": "计算机",
    "confluence": "合流",
    "categorically": "范畴地",
    "consistency": "一致性",
    "defined": "定义的",
    "explicit": "显式",
    "terms": "项",
    "cotransitivity": "余传递",
    "counit": "余单位",
    "laws": "律",
    "decode": "解码",
    "defining": "定义",
    "adverbs": "副词",
    "direct": "直接",
    "denial": "否认",
    "dense": "稠密",
    "depression": "下降",
    "data": "数据",
    "disc": "圆盘",
    "union": "并集",
    "encode": "编码",
    "epi": "epi",
    "net": "网",
    "reflexivity": "自反",
    "symmetry": "对称",
    "transitivity": "传递",
    "equipped": "配备",
    "properties": "性质",
    "evaluation": "求值",
    "evidence": "证据",
    "evil": "邪恶",
    "extraction": "抽取",
    "algorithms": "算法",
    "orthogonal": "正交",
    "false": "假",
    "fibrant": "纤维化良好",
    "signature": "签名",
    "topology": "拓扑",
    "formalization": "形式化",
    "generation": "生成",
    "bijective": "双射",
    "idempotent": "幂等",
    "functional": "函数式",
    "extension": "扩展",
    "geometric": "几何",
    "realization": "实现",
    "geometry": "几何",
    "globular": "球状",
    "h-level": "h-层级",
    "h-proposition": "h-命题",
    "helix": "螺旋",
    "hom-functor": "hom-函子",
    "homology": "同调",
    "algebras": "代数",
    "junior": "初级",
    "transformations": "变换",
    "hub": "枢纽",
    "at": "在",
    "implementation": "实现",
    "impredicativity": "非直谓性",
    "inaccessible": "不可达",
    "index": "索引",
    "indiscrete": "粗离散",
    "infix": "中缀",
    "characterization": "刻画",
    "frame": "框架",
    "interchange": "交换",
    "left": "左",
    "right": "右",
    "isometry": "等距",
    "invariance": "不变性",
    "transfer": "转移",
    "across": "跨",
    "simplicial": "单纯",
    "klein": "Klein",
    "bottle": "瓶",
    "calculus": "演算",
    "lax": "lax",
    "least": "最小",
    "locale": "locale",
    "localization": "局部化",
    "locatedness": "定位性",
    "location": "位置",
    "traditional": "传统",
    "functoriality": "函子性",
    "iterated": "迭代",
    "spans": "跨图",
    "cone": "锥",
    "formalized": "形式化",
    "meridian": "子午线",
    "metrically": "度量地",
    "compact": "紧致",
    "convergence": "收敛",
    "uniform": "一致",
    "monad": "单子",
    "mono": "mono",
    "monotonicity": "单调性",
    "definable": "可定义",
    "nonempty": "非空",
    "noun": "名词",
    "problem": "问题",
    "option": "选项",
    "order-dense": "序稠密",
    "unordered": "无序",
    "paradox": "悖论",
    "parentheses": "括号",
    "partial": "偏",
    "composite": "复合",
    "lifting": "提升",
    "pentagon": "五边形",
    "functionality": "功能性",
    "operations": "运算",
    "polarity": "极性",
    "pole": "极点",
    "poset": "偏序集",
    "tower": "塔",
    "predecessor": "前驱",
    "preorder": "预序",
    "its": "其",
    "prime": "素",
    "programming": "编程",
    "projective": "射影",
    "plane": "平面",
    "purely": "纯粹",
    "agree": "一致",
    "homotopical": "同伦的",
    "red": "红",
    "herring": "鲱鱼",
    "reduced": "约化",
    "reflection": "反射",
    "subcategory": "子范畴",
    "antisymmetric": "反对称",
    "effective": "有效",
    "irreflexive": "非自反",
    "monotonic": "单调",
    "reflexive": "自反",
    "rounded": "圆整",
    "symmetric": "对称",
    "transitive": "传递",
    "formation": "形成",
    "introduction": "引入",
    "axioms": "公理",
    "setoid": "setoid",
    "first-order": "一阶",
    "cw-complex": "CW-复形",
    "squaring": "平方",
    "stages": "阶段",
    "five": "五",
    "abuse": "滥用",
    "action": "作用",
    "addition": "加法",
    "admissible": "可容许",
    "adjoint": "伴随",
    "analysis": "分析",
    "application": "应用",
    "automorphism": "自同构",
    "distance": "距离",
    "element": "元素",
    "natural": "自然",
    "procedure": "过程",
    "type-theoretic": "类型论的",
    "non-dependent": "非依值",
    "predicative": "直谓",
    "impredicative": "非直谓",
    "boolean": "布尔",
    "pointfree": "无点",
    "recursive": "递归",
    "generalizations": "推广",
    "negative": "负",
    "members": "成员",
    "singleton": "单点集",
    "captured": "被捕获",
    "informal": "非形式",
    "intensional": "内涵",
    "unequal": "不等",
    "proofs": "证明",
    "finite": "有限",
    "subfamily": "子族",
    "reflective": "反射",
    "precategories": "预范畴",
    "vary": "变化",
    "along": "沿",
    "vertex": "顶点",
    "standard": "标准",
    "accepting": "接受",
    "flattening": "扁平化",
    "simplicity": "简单性",
    "commutative": "交换",
    "containment": "包含",
    "dimension": "维度",
    "elementary": "初等",
    "factorization": "分解",
    "game": "游戏",
    "generator": "生成元",
    "inclusion": "包含映射",
    "infinitary": "无穷元",
    "intersection": "交集",
    "irreflexivity": "非自反性",
    "iterator": "迭代器",
    "modulus": "模",
    "nullary": "零元",
    "ordinals": "序数",
    "parameter": "参数",
    "presentation": "表示",
    "retract": "缩回",
    "skeleton": "骨架",
    "source": "源",
    "target": "靶",
    "supremum": "上确界",
    "terminal": "终对象",
    "total": "全",
    "tree": "树",
    "winding": "绕行",
    "witness": "见证",
    "naturality": "自然性",
    "unstable": "不稳定",
    "cotransitive": "余传递",
    "alexandria": "Alexandria",
    "operad": "operad",
    "setoid": "setoid",
    "locale": "locale",
    "epi": "epi",
    "mono": "mono",
    "gaunt": "Gaunt",
    "pseudo-": "伪",
}

# Keep personal names in Latin script per translation rule.
KEEP_NAME_CANONICAL: Dict[str, str] = {
    "cauchy": "Cauchy",
    "dedekind": "Dedekind",
    "yoneda": "Yoneda",
    "quillen": "Quillen",
    "grothendieck": "Grothendieck",
    "hopf": "Hopf",
    "rezk": "Rezk",
    "kan": "Kan",
    "hedberg": "Hedberg",
    "eckmann": "Eckmann",
    "hilton": "Hilton",
    "conway": "Conway",
    "frege": "Frege",
    "freudenthal": "Freudenthal",
    "lawvere": "Lawvere",
    "peano": "Peano",
    "bourbaki": "Bourbaki",
    "automath": "AUTOMATH",
    "haskell": "Haskell",
    "blakers": "Blakers",
    "massey": "Massey",
    "escard": "Escardó",
    "simpson": "Simpson",
    "diaconescu": "Diaconescu",
    "feit": "Feit",
    "thompson": "Thompson",
    "euclid": "Euclid",
    "bolzano": "Bolzano",
    "weierstra": "Weierstraß",
    "heine": "Heine",
    "borel": "Borel",
    "cantor": "Cantor",
    "lipschitz": "Lipschitz",
    "markov": "Markov",
    "whitehead": "Whitehead",
    "postnikov": "Postnikov",
    "kampen": "Kampen",
    "schroeder": "Schroeder",
    "bernstein": "Bernstein",
    "stone": "Stone",
    "segal": "Segal",
    "galois": "Galois",
    "lebesgue": "Lebesgue",
    "martin-l": "Martin-Löf",
    "streicher": "Streicher",
    "russell": "Russell",
    "bertrand": "Bertrand",
    "scott": "Scott",
    "ackermann": "Ackermann",
    "morgan": "Morgan",
    "mac": "Mac",
    "lane": "Lane",
    "tierney": "Tierney",
    "van": "van",
    "alexandria": "Alexandria",
}

EXACT_TERM: Dict[str, str] = {
    "abuse": "滥用",
    "action": "作用",
    "addition": "加法",
    "adjoint": "伴随",
    "admissible": "可容许",
    "algebra": "代数",
    "analysis": "分析",
    "application": "应用",
    "automorphism": "自同构",
    "axiom": "公理",
    "distance": "距离",
    "element": "元素",
    "procedure": "过程",
    "natural": "自然",
    "locale": "locale",
    "operad": "operad",
    "setoid": "setoid",
}


def compile_phrase_patterns(term_table: Dict[str, str]) -> List[Tuple[re.Pattern[str], str]]:
    merged = dict(term_table)
    merged.update({normalize_key(k): v for k, v in EXTRA_PHRASE.items()})
    items = sorted(merged.items(), key=lambda kv: (-len(kv[0]), kv[0]))
    return [
        (re.compile(rf"(?<![A-Za-z]){re.escape(en)}(?![A-Za-z])", re.I), zh)
        for en, zh in items
    ]


def protect_tex(text: str) -> Tuple[str, List[str]]:
    protected: List[str] = []

    def sub(m: re.Match[str]) -> str:
        protected.append(m.group(0))
        return f"__P{len(protected)-1}__"

    text = re.sub(r"\$[^$]*\$", sub, text)
    text = re.sub(r"\\[A-Za-z@]+\*?(?:\s*\{[^{}]*\})*", sub, text)
    return text, protected


def unprotect_tex(text: str, protected: List[str]) -> str:
    for i, seg in enumerate(protected):
        text = text.replace(f"__P{i}__", seg)
    return text


def rewrite_leading_particles(text: str) -> str:
    m = re.match(r"^的\s+(.+)$", text)
    if m:
        return f"{m.group(1)}的"
    m = re.match(r"^中\s+(.+)$", text)
    if m:
        return f"{m.group(1)}中"
    m = re.match(r"^上\s+(.+)$", text)
    if m:
        return f"{m.group(1)}上"
    m = re.match(r"^下\s+(.+)$", text)
    if m:
        return f"{m.group(1)}下"
    return text


def cleanup_cjk_spacing(text: str) -> str:
    # Remove spacing artifacts from word-by-word translation while keeping
    # spacing around Latin names/abbreviations.
    text = re.sub(r"(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])", "", text)
    text = re.sub(r"(?<=[\u4e00-\u9fff])\s+(?=[，。；：、）】》〉])", "", text)
    text = re.sub(r"(?<=[（【《〈])\s+(?=[\u4e00-\u9fffA-Za-z0-9])", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def translate_term(term: str, phrase_patterns: List[Tuple[re.Pattern[str], str]]) -> str:
    normalized_term = normalize_key(term)
    if normalized_term in EXACT_TERM:
        return EXACT_TERM[normalized_term]

    text = re.sub(r"([A-Za-z][A-Za-z\-]*)'s", r"\1 的", term)
    text, protected = protect_tex(text)

    for reg, zh in phrase_patterns:
        text = reg.sub(lambda _m, z=zh: z, text)

    def word_sub(m: re.Match[str]) -> str:
        w = m.group(0)
        lw = w.lower()
        if lw in KEEP_NAME_CANONICAL:
            return KEEP_NAME_CANONICAL[lw]
        if lw in WORD:
            return WORD[lw]
        return w

    text = re.sub(r"[A-Za-z][A-Za-z\-]*", word_sub, text)
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace(" ,", ",")
    text = re.sub(r"\s+,", ",", text)
    text = re.sub(r",\s+", ", ", text)
    text = rewrite_leading_particles(text)
    text = cleanup_cjk_spacing(text)

    return unprotect_tex(text, protected)


def translate_see_targets(rest: str, phrase_patterns: List[Tuple[re.Pattern[str], str]]) -> str:
    def sub(m: re.Match[str]) -> str:
        kind, body = m.group(1), m.group(2)
        return f"\\{kind}" + "{" + translate_term(body, phrase_patterns) + "}"

    return re.sub(r"\\(see|seealso)\{([^}]*)\}", sub, rest)


def translate_ind_content(content: str, phrase_patterns: List[Tuple[re.Pattern[str], str]]) -> str:
    out: List[str] = []

    # Case A: term and hyper refs on same line.
    p_inline = re.compile(r"^(\s*\\(?:item|subitem|subsubitem)\s+)(.+?)(,\s*\\hyper.*)$")
    # Case B: line ends with comma, refs continue next line.
    p_wrap = re.compile(r"^(\s*\\(?:item|subitem|subsubitem)\s+)(.+)(,\s*)$")
    # Case C: parent index entry with subentries only (no refs on this line).
    p_bare = re.compile(r"^(\s*\\(?:item|subitem|subsubitem)\s+)(.+?)\s*$")

    for line in content.splitlines():
        m = p_inline.match(line)
        if m:
            pre, term, rest = m.groups()
            line = pre + translate_term(term, phrase_patterns) + translate_see_targets(rest, phrase_patterns)
        else:
            m = p_wrap.match(line)
            if m:
                pre, term, rest = m.groups()
                line = pre + translate_term(term, phrase_patterns) + rest
            else:
                m = p_bare.match(line)
                if m and "\\hyper" not in line:
                    pre, term = m.groups()
                    line = pre + translate_term(term, phrase_patterns)
        out.append(line)

    return "\n".join(out) + "\n"


def count_english_terms(content: str) -> int:
    p = re.compile(r"^\s*\\(?:item|subitem|subsubitem)\s+(.+?)(?:,\s*\\hyper.*|,\s*)$", re.M)
    count = 0
    for m in p.finditer(content):
        term = m.group(1)
        term = re.sub(r"\$[^$]*\$", "", term)
        term = re.sub(r"\\[A-Za-z@]+\*?(?:\s*\{[^{}]*\})*", "", term)
        # Ignore pure personal names (capitalized tokens) by only counting lowercase english leftovers.
        if re.search(r"[a-z]{2,}", term):
            count += 1
    return count


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: translate_index_cn.py IN_IND TERMINOLOGY_MD OUT_IND")
        return 2

    in_ind = Path(sys.argv[1])
    term_md = Path(sys.argv[2])
    out_ind = Path(sys.argv[3])

    if not in_ind.exists():
        print(f"index file not found: {in_ind}")
        return 1
    if not term_md.exists():
        print(f"terminology file not found: {term_md}")
        return 1

    phrase_patterns = compile_phrase_patterns(load_term_table(term_md))

    src = in_ind.read_text(encoding="utf-8")
    dst = translate_ind_content(src, phrase_patterns)
    out_ind.write_text(dst, encoding="utf-8")

    print(f"english_terms_before={count_english_terms(src)}")
    print(f"english_terms_after={count_english_terms(dst)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
