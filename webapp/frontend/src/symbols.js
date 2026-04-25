// All available symbols from the component library.
// Each key is the filename stem; value is the public path.
export const ALL_SYMBOLS = Object.fromEntries([
  'b-bsp','b-bspcube','b-coupler','b-crystalcc','b-crystalfc','b-crystalff',
  'b-diccube','b-dicgrn','b-dicred','b-dump','b-grat',
  'b-lens1','b-lens2','b-lens3','b-mir','b-mirc','b-mircpzt','b-mirpzt',
  'b-npro','b-phase','b-wpgn','b-wpred','b-wpyel',
  'c-aom','c-diodegrn','c-eom1','c-eom2','c-fiber','c-fibercoupl',
  'c-flip','c-isolator','c-laser1','c-laser2','c-mirpzt3ax',
  'c-modeclean','c-modecleanpzt',
  'c-opacc','c-opaccplates','c-opacfplates','c-opafc','c-opaff',
  'c-opaffplates','c-opakerr','c-opared','c-rotator',
  'e-amp','e-computer','e-diff','e-frq1','e-frq2',
  'e-hipass','e-hvampleft','e-hvampright','e-lopass','e-mix',
  'e-pd1','e-pd2','e-pdgrn1','e-pdgrn2','e-qpd',
  'e-servoleft','e-servoright','e-spekki','e-sum','e-sumdiff',
].map(name => [name, `/symbols/${name}.svg`]))
